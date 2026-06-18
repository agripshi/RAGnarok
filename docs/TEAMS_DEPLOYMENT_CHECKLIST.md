# RAGnarok — Teams Deployment Checklist

This checklist covers moving from **local sideload demo** to **org-ready Teams deployment**.

---

## Current state (MVP v1.0)

| Capability | Local demo | Production Teams |
|------------|------------|------------------|
| Teams manifest + icons | Yes | Needs HTTPS URLs |
| Sideload on your PC | Yes | N/A |
| Chat + RAG | Yes | Needs hosted API/AI |
| Teams SSO | Dev token fallback | Not implemented |
| Graph channel access | Email allowlist | Not implemented |
| Database | SQLite (local) | PostgreSQL required |
| Vector store | In-memory | Qdrant / Chroma cloud |

---

## Phase A — Local sideload (hackathon demo)

Use this today. No Azure required.

### Prerequisites

- [ ] Node.js 20+, Python 3.11+
- [ ] Tenant allows custom app upload (or use Teams Toolkit dev tenant)
- [ ] All three services running on your machine

### Steps

1. **Start services**
   ```powershell
   .\scripts\start-dev.ps1
   ```
   Or manually: AI `:8001` → API `:8000` → Web `:5173`

2. **Configure frontend** — copy `apps/web/.env.example` → `apps/web/.env.local`:
   ```env
   VITE_API_BASE_URL=http://127.0.0.1:8000
   VITE_ENABLE_TEAMS_AUTH=false
   VITE_ENABLE_MOCK_TEAMS_SHELL=true
   VITE_DEV_AUTH_TOKEN=dev-token
   ```

3. **Package manifest** — zip these files from `apps/web/appPackage/`:
   - `manifest.json`
   - `color.png`
   - `outline.png`

4. **Upload to Teams**
   - Teams → Apps → Manage your apps → **Upload a custom app**
   - Select the zip file
   - Pin/open the **HR Assistant** tab

5. **Verify**
   - [ ] Tab loads (no infinite spinner)
   - [ ] `/api/me` returns `hasHrAccess: true`
   - [ ] Italian question returns `ANSWERED` + source card
   - [ ] Guardrail question returns `NOT_FOUND`

6. **Demo script** — see `docs/DEMO.md`

### Local sideload limitations

- Works only on the machine running the dev servers
- Uses `dev-token`, not real Teams SSO
- `127.0.0.1` in manifest — other users cannot access your localhost

---

## Phase B — Azure hosting (required for real deployment)

### B1. Microsoft Entra ID app registration

- [ ] Create app registration in [Azure Portal](https://portal.azure.com) → Microsoft Entra ID → App registrations
- [ ] Note **Application (client) ID** → use as manifest `webApplicationInfo.id`
- [ ] Generate new **Application ID URI**: `api://<your-domain>/<client-id>`
- [ ] Add redirect URIs for Teams SSO (see [Teams SSO docs](https://learn.microsoft.com/en-us/microsoftteams/platform/tabs/how-to/authentication/tab-sso-overview))
- [ ] Expose API scope: `access_as_user`
- [ ] Grant admin consent for your tenant
- [ ] Add API permissions: `User.Read`, Microsoft Graph channel/membership scopes for OBO

### B2. Deploy frontend (HTTPS)

Recommended: **Azure Static Web Apps** or **Azure App Service**

- [ ] Build: `cd apps/web && npm run build`
- [ ] Deploy `dist/` to HTTPS host (e.g. `https://ragnarok-hr.azurestaticapps.net`)
- [ ] Set production env:
  ```env
  VITE_API_BASE_URL=https://api.your-domain.com
  VITE_ENABLE_TEAMS_AUTH=true
  VITE_ENABLE_MOCK_TEAMS_SHELL=false
  ```

### B3. Deploy backend API

Recommended: **Azure App Service** or **Azure Container Apps**

- [ ] Deploy `apps/api` with production `.env`:
  ```env
  APP_ENV=production
  DATABASE_URL=postgresql+psycopg://...
  AI_BACKEND_URL=https://ai.your-domain.com
  AI_BACKEND_INTERNAL_TOKEN=<strong-secret>
  FRONTEND_ORIGINS=https://ragnarok-hr.azurestaticapps.net
  DEV_AUTH_ENABLED=false
  TEAM_ID=<your-teams-team-id>
  HR_PRIVATE_CHANNEL_ID=<your-hr-channel-id>
  AUTHORIZED_EMAILS=  # remove for Graph-based access
  ```
- [ ] Run Alembic migrations: `alembic upgrade head`
- [ ] Verify: `GET https://api.your-domain.com/api/health`

### B4. Deploy AI backend

- [ ] Deploy `apps/ai` (separate App Service or container)
- [ ] Set production `.env`:
  ```env
  VECTOR_DB=qdrant
  QDRANT_URL=https://...
  LLM_API_KEY=<azure-openai-or-openai-key>
  LLM_MOCK_ENABLED=false
  AI_BACKEND_INTERNAL_TOKEN=<same-as-api>
  ```
- [ ] Run initial ingest: `POST /ai/ingest/sync`
- [ ] Verify: `GET https://ai.your-domain.com/ai/health`

### B5. Data layer

- [ ] PostgreSQL (Azure Database for PostgreSQL)
- [ ] Qdrant Cloud or self-hosted Qdrant
- [ ] Upload HR docs to SharePoint / Teams channel for Graph sync (future)

---

## Phase C — Update Teams manifest

Edit `apps/web/appPackage/manifest.json`:

```json
{
  "id": "<new-guid-for-production>",
  "version": "1.0.0",
  "staticTabs": [{
    "contentUrl": "https://ragnarok-hr.azurestaticapps.net",
    "websiteUrl": "https://ragnarok-hr.azurestaticapps.net"
  }],
  "validDomains": [
    "ragnarok-hr.azurestaticapps.net",
    "api.your-domain.com"
  ],
  "webApplicationInfo": {
    "id": "<entra-client-id>",
    "resource": "api://ragnarok-hr.azurestaticapps.net/<entra-client-id>"
  }
}
```

- [ ] Replace placeholder GUIDs (`00000000-...`)
- [ ] Use **HTTPS** only (Teams blocks mixed content)
- [ ] Add privacy/terms URLs (real pages, not github.com placeholders)
- [ ] Re-zip and upload (sideload) or submit via **Teams Admin Center**

---

## Phase D — Implement production auth (code changes)

These are **not** in the MVP; required before org rollout.

### D1. Teams SSO token validation (backend)

- [ ] Add `msal` / `PyJWT` validation in `apps/api/app/services/auth_service.py`
- [ ] Validate JWT from `Authorization: Bearer <teams-sso-token>`
- [ ] Exchange for Graph token via OBO flow
- [ ] Remove `dev-token` path when `DEV_AUTH_ENABLED=false`

### D2. Graph channel membership (access guard)

- [ ] Replace email allowlist in `access_guard.py`
- [ ] Call Microsoft Graph: verify user is member of `HR_PRIVATE_CHANNEL_ID`
- [ ] Cache result in `access_check_cache` table (TTL already exists)

### D3. Frontend production auth

- [ ] Set `VITE_ENABLE_TEAMS_AUTH=true` in production build
- [ ] Remove dev-token fallback in production bundle
- [ ] Handle SSO token refresh via `teams.authentication.getAuthToken()`

### D4. CORS & security hardening

- [ ] Remove `allow_origins=["*"]` for `APP_ENV=production`
- [ ] Lock `FRONTEND_ORIGINS` to deployed domain only
- [ ] Rotate `AI_BACKEND_INTERNAL_TOKEN`
- [ ] Enable HTTPS-only cookies if using session auth

---

## Phase E — Org distribution

### Option 1: Custom app (single tenant)

- [ ] Teams Admin Center → Teams apps → Upload custom app
- [ ] Assign to HR security group
- [ ] Pin tab in private HR channel

### Option 2: Organization catalog

- [ ] Validate manifest with [Teams Toolkit](https://learn.microsoft.com/en-us/microsoftteams/platform/toolkit/teams-toolkit-fundamentals)
- [ ] Submit for admin approval in Teams Admin Center
- [ ] Publish internally via **Manage apps**

### Option 3: AppSource (future)

- [ ] Partner Center registration
- [ ] Security/compliance review
- [ ] Multi-tenant Entra configuration

---

## Pre-flight test matrix

| Test | Local | Production |
|------|-------|------------|
| App loads in Teams tab | ✓ | |
| SSO login (no dev-token) | | |
| `/api/me` returns user | ✓ | |
| Chat ANSWERED + sources | ✓ | |
| NOT_FOUND guardrail | ✓ | |
| Access denied (non-member) | partial (allowlist) | |
| Feedback saved | ✓ | |
| Admin ingest trigger | ✓ | |
| Albanian / Italian / Serbian | partial | |

---

## Quick reference — ports & URLs (local)

| Service | URL |
|---------|-----|
| Frontend | http://127.0.0.1:5173 |
| Backend API | http://127.0.0.1:8000 |
| AI backend | http://127.0.0.1:8001 |
| Health checks | `/api/health`, `/ai/health` |

---

## Related docs

- `docs/DEMO.md` — 10-minute judge demo script
- `docs/RAGnarok_Technical_Architecture_Spec.md` — full architecture
- `README.md` — local setup and sprint status
