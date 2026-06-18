# RAGnarok — Teams Channel Document Access Verification

**Date:** 2026-06-18
**Question:** Given a real Teams channel deep link, would the application be able to obtain **full access to the documents stored in that channel**?
**Verdict:** ❌ **No.** The codebase has **no Microsoft Graph / SharePoint integration**. Document ingestion reads only from a local filesystem directory; it cannot read files from a Teams channel.

---

## 1. Target channel (from the provided deep link)

| Field | Value |
|-------|-------|
| Channel name | `Documents - Engineering Albania` |
| Channel ID | `19:11b56c75623d48ac828e2797373cacae@thread.tacv2` |
| Team / group ID | `1531e68a-4716-43aa-bc3b-41b11451cbbb` |
| Tenant ID | `f2d7d6c5-1bee-41ff-9e79-b372a5cce71d` |

> Note: `@thread.tacv2` denotes a **standard** channel. Its files physically live in the team's SharePoint document library, under a folder named after the channel.

---

## 2. Verdict

The application **cannot** access the documents in this (or any) Teams channel. There is no Graph/SharePoint client, no OAuth/OBO token acquisition, and no drive/site enumeration anywhere in the code. Document ingestion is **local-filesystem only**.

Passing the real `channelId` / `groupId` into the system would **not** fetch anything from the channel — those values are used purely as metadata tags on locally ingested chunks.

---

## 3. Evidence (code-level)

### 3.1 Ingestion accepts only a local source — enforced by the type

`apps/ai/app/schemas/ingest.py`
```python
class IngestRequest(BaseModel):
    source_mode: Literal["local"] = "local"   # rejects "graph"/"sharepoint" at validation time
    source_path: str | None = None
    team_id: str
    channel_id: str
    force_reindex: bool = False
```

### 3.2 Ingestion iterates a directory on disk

`apps/ai/app/services/ingestion_service.py`
```python
source = Path(request.source_path or settings.hr_docs_local_dir).resolve()
if not source.exists():
    return IngestResponse(status="error", errors=[f"Source path not found: {source}"])
...
for path in sorted(source.iterdir()):       # local filesystem only
    if not path.is_file() or path.suffix.lower() not in SUPPORTED:
        continue
```
- Supported types: `.pdf`, `.docx`, `.txt`, `.md` (`pipeline.SUPPORTED`).
- Default directory: `hr_docs_local_dir = "../../data/hr-docs"` (`apps/ai/app/core/config.py`).

### 3.3 `team_id` / `channel_id` are metadata only — not a data source

In `ingestion_service.py` they are written onto each `ChunkRecord` (used later to filter retrieval), never used to locate or download channel content:
```python
ChunkRecord(
    ...
    team_id=request.team_id,
    channel_id=request.channel_id,
    ...
)
```

### 3.4 The API orchestrator hardcodes the local mode

`apps/api/app/services/ingestion_orchestrator.py`
```python
payload = {
    "source_mode": "local",
    "team_id": settings.team_id,
    "channel_id": settings.hr_private_channel_id,
    "force_reindex": True,
}
```

### 3.5 No Graph configuration is consumed by code

`apps/ai/app/core/config.py` contains only Qdrant/Chroma/LLM/embedding settings plus `hr_docs_local_dir`. The `GRAPH_BASE_URL` / `GRAPH_SCOPES` variables in `apps/api/.env.example` are **declared but never read by any code**.

### 3.6 Repository-wide search confirms the absence

A search across all `*.py` files for `graph.microsoft`, `filesFolder`, `/drives`, `/sites`, `msal`, `ConfidentialClient`, `/teams/` returned **no matches**.

---

## 4. What full channel access would require

To actually read the documents in `Documents - Engineering Albania`, the following would have to be built from scratch:

1. **Entra app registration** in tenant `f2d7d6c5-1bee-41ff-9e79-b372a5cce71d` with admin consent.
2. **Microsoft Graph permissions** — application permissions `Files.Read.All` / `Sites.Read.All` (or `Sites.Selected`) and, for membership-scoped logic, `ChannelMember.Read.All`; or a delegated / on-behalf-of (OBO) flow.
3. **Token acquisition** — MSAL confidential client (client credentials or OBO).
4. **Graph calls to resolve and enumerate channel files:**
   - `GET /teams/{groupId}/channels/{channelId}/filesFolder` → returns the backing `driveItem` (drive + item ID).
   - `GET /drives/{driveId}/items/{itemId}/children` → enumerate files.
   - `GET /drives/{driveId}/items/{itemId}/content` → download each file.
5. **A new `source_mode`** (e.g. `"graph"`) in `IngestRequest`, plus a loader that downloads the binaries and feeds them into the existing extraction/chunking pipeline.

---

## 5. Related gap

This is consistent with finding **I3** in `TEAMS_INTEGRATION_VERIFICATION_REPORT.md`: `graph_access_service.py` is missing. As a result, **neither** ingestion **from** the channel **nor** membership verification **against** the channel is implemented — both depend on Microsoft Graph, which is entirely absent.

---

## 6. Summary

| Capability | Status |
|------------|--------|
| Read/ingest documents from a Teams channel (SharePoint library) | ❌ Not implemented |
| Ingest documents from a local folder | ✅ Implemented (`source_mode="local"`) |
| Use `team_id` / `channel_id` to scope retrieval | ✅ As metadata tags only |
| Verify user membership of the channel via Graph | ❌ Not implemented (allowlist only) |
| Microsoft Graph / SharePoint client present in code | ❌ Absent |
