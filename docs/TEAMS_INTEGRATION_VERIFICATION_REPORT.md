# RAGnarok — Teams Integration Verification Report

**Date:** 2026-06-18
**Scope:** Verification of all documents under `docs/` and review of the Microsoft Teams connection/integration across the codebase.
**Reviewer profile:** Applied the project's `code-reviewer-agent` role (correctness, security, layer boundaries, DTO contracts), supplemented by the `infra-agent` role for the Teams manifest and SSO packaging.
**IMPACT skill:** Not used. IMPACT is intended for full architectural reverse-engineering; for this focused Teams-integration bug/gap check a targeted review was sufficient.

---

## 1. Method

1. Enumerated and read all 10 documents in `docs/`.
2. Reviewed the project's custom agents under `agents/` to select the most suitable reviewer profile.
3. Traced the real Teams integration flow through the code:
   - Frontend Teams SDK init, SSO token acquisition, and context — `apps/web/src/auth/teamsAuth.ts`, `useTeamsAuth.ts`, `config/env.ts`
   - Teams app package — `apps/web/appPackage/manifest.json`
   - API client and chat flow — `apps/web/src/api/*`, `components/chat/ChatPage.tsx`, `App.tsx`
   - Backend authentication, access guard, chat orchestration — `apps/api/app/services/auth_service.py`, `access_guard.py`, `chat_service.py`, `ai_client.py`, `core/config.py`, `api/routes/me.py`
   - Environment templates — `apps/*/.env.example`
4. Ran the real frontend typecheck (`tsc -b`) to confirm suspected build failures.

---

## 2. Executive summary

The Teams **design** is sound — authorization is enforced server-side using configured `team_id`/`channel_id` (not values trusted from the client), the access guard runs before every AI call, and the SSO token is kept in memory only.

However, the **frontend currently does not build**, which blocks producing the Teams app package entirely. Two of the three build errors are trivial to fix; one of them is also a genuine Teams-SSO logic bug. Production Teams auth (Entra JWT validation + Microsoft Graph channel membership) is documented as future work and is not implemented, which is expected for the MVP but leaves several declared environment variables unused.

---

## 3. Findings

### 🔴 BLOCKER — Frontend build is broken (Teams app package cannot be produced)

`npm run build` (`tsc -b && vite build`) fails with three errors:

| # | Location | Error | Detail |
|---|----------|-------|--------|
| B1 | `apps/web/src/auth/useTeamsAuth.ts:22` | `TS2554: Expected 1 arguments, but got 0` | `refreshToken` calls `getTeamsSsoToken()` without the required `inTeams: boolean` argument. The initial load (line 37) correctly passes `inTeams`. This is both a compile error **and** a logic bug: on token refresh the dev-token vs. real-SSO selection (`shouldUseDevToken`) receives `undefined` and can pick the wrong path. Fix: pass `isRunningInTeams`. |
| B2 | `apps/web/src/api/apiClient.ts:6-7` | `TS1294: This syntax is not allowed when 'erasableSyntaxOnly' is enabled` | TypeScript parameter properties (`public readonly status`, `public readonly payload`) are not allowed under `erasableSyntaxOnly: true`. Fix: declare the fields explicitly and assign them in the constructor body. `erasableSyntaxOnly` may surface additional occurrences once this is resolved. |

**Impact:** `apps/web/dist` cannot be produced, so the Teams sideload package (Phase A) and any Azure deployment (Phase B) of the `TEAMS_DEPLOYMENT_CHECKLIST.md` cannot proceed as-is.

### 🟡 IMPORTANT

- **I1 — SSO token refresh is never triggered.** `apiClient.apiFetch` does not call `refreshToken` on `401`. When the SSO token expires, the user is stuck with no retry. Consistent with checklist item D3 ("not in MVP"), but worth flagging.
- **I2 — Manifest `webApplicationInfo` is internally inconsistent.** `resource: "api://localhost:53000/<id>"` uses a host/port (`localhost:53000`) that is **not** in `validDomains` and differs from `contentUrl` (`http://127.0.0.1:5173`). With real SSO enabled this breaks token acquisition. Must be aligned in Phase C before production.
- **I3 — `graph_access_service.py` is missing.** Both `agents/backend-api-agent.md` and the access-guard design describe a production branch ("production → GraphAccessService: OBO flow + Graph channel membership"), but `access_guard.py` implements **only** the email/ID allowlist. Env vars `TENANT_ID`, `BACKEND_CLIENT_ID`, `BACKEND_CLIENT_SECRET`, `GRAPH_*`, and `EXPECTED_TOKEN_AUDIENCE` are declared but unused by any code. Documented as future work (D1/D2), but it is a gap versus the agent specifications.
- **I4 — Backend accepts only `dev-token`.** `auth_service.authenticate` performs no Entra JWT validation (signature / exp / issuer / audience); any non-`dev-token` is rejected. Expected for the MVP, but it means **no real Teams SSO token works today**.

### 🔵 SUGGESTION / Documentation hygiene

- **S1 — Locale is not normalized.** `getTeamsContext` forwards `ctx.app.locale` (e.g. `"it-IT"`) as `response_language_hint`, while supported languages are `it` / `sq` / `sr`. Confirm the AI backend normalizes the hint, otherwise it is ineffective.
- **S2 — Duplicate documents.** `RAGnarok_Technical_Architecture_Spec (1).md` and `RAGnarok_Business_Foundational_Spec (1).md` appear to be accidental copies of their originals.
- **S3 — Minor docs↔config mismatch.** `TEAMS_DEPLOYMENT_CHECKLIST.md` uses `VITE_API_BASE_URL=http://127.0.0.1:8000`, while `apps/web/.env.example` uses `http://localhost:8000`. Both are covered by backend CORS, but the inconsistency is confusing.

---

## 4. What is correct (verified)

- AI `authorization_scope` uses `settings.team_id` / `settings.hr_private_channel_id`, **not** the frontend-supplied `teamsContext` — fail-closed, no client trust (`apps/api/app/services/chat_service.py`).
- Access guard runs before any AI call, on both `POST /api/chat` and `GET /api/me`.
- SSO token is kept in memory only (no `localStorage` / `sessionStorage`); no secrets in the frontend env.
- `AI_BACKEND_INTERNAL_TOKEN` is consistent between `apps/api/.env.example` and the AI backend; the raw frontend bearer token is never forwarded to the AI backend.

---

## 5. Recommended fix order

1. **B1 + B2** — restore the frontend build (smallest, safe changes; unblocks the Teams package).
2. **I2** — align manifest `webApplicationInfo.resource` / `validDomains` / `contentUrl` before any SSO testing.
3. **I3 + I4** — implement Entra JWT validation and `GraphAccessService` (OBO + channel membership) when moving beyond the MVP allowlist.
4. **I1, S1** — wire SSO refresh on `401`; normalize locale to a supported language code.
5. **S2, S3** — remove duplicate docs; align the API base URL between checklist and `.env.example`.

---

## 6. Verified commands

- Frontend typecheck / build: `cd apps/web && npm run build` (runs `tsc -b && vite build`) — currently **fails** with errors B1 and B2 above.
