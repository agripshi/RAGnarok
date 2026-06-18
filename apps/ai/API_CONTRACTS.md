# RAGnarok AI Backend — API Contracts

Base URL: `http://127.0.0.1:8001` (configurable via `AI_PORT`)

All routes are prefixed with `/ai`.

---

## Authentication

| Route group | Auth |
|-------------|------|
| `GET /ai/health` | None |
| `POST /ai/ingest/sync`, `POST /ai/rag/answer` | `Authorization: Bearer <AI_BACKEND_INTERNAL_TOKEN>` |
| `POST /ai/test/*` | None — only registered when `TEST_MODE=true` |

Default token (local): `dev-internal-token`

---

## Location model

HR documents live under branch subfolders:

```text
HR_DOCS_LOCAL_DIR/
  al/    ← Albania branch
  sr/    ← Serbia branch
```

| Value | Branch | Default language | Docs folder |
|-------|--------|------------------|-------------|
| `al` | Albania | `sq` | `{HR_DOCS_LOCAL_DIR}/al/` |
| `sr` | Serbia | `sr` | `{HR_DOCS_LOCAL_DIR}/sr/` |

- **Ingest:** each chunk is tagged with `location` from its parent folder.
- **RAG query:** `location` is **required**; retrieval returns only chunks matching that branch.

---

## Endpoints

### GET /ai/health

**Purpose:** Service liveness and configuration summary.

**Auth:** None

**Response 200:**

```json
{
  "status": "ok",
  "service": "ragnarok-ai-backend",
  "testMode": true,
  "vectorDb": "chroma",
  "embeddingProvider": "openai",
  "embeddingModel": "text-embedding-3-small",
  "llmMode": "cloud",
  "llmModel": "gpt-4o-mini"
}
```

---

### POST /ai/ingest/sync

**Purpose:** Load documents from `al/` and `sr/` subfolders, split/chunk, embed, and store in the vector DB.

**Auth:** Bearer token required

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source_mode` | `"local"` | No (default `"local"`) | Ingest source type |
| `source_path` | string \| null | No | Override docs root; default `HR_DOCS_LOCAL_DIR` |
| `team_id` | string | Yes | Scope tag stored on every chunk |
| `channel_id` | string | Yes | Scope tag stored on every chunk |
| `location` | `"al"` \| `"sr"` \| null | No | If set, ingest only that subfolder; if omitted, ingest both |
| `force_reindex` | boolean | No (default `false`) | Re-index even if file hash unchanged |

**Example:**

```json
{
  "source_mode": "local",
  "source_path": null,
  "team_id": "demo-team-id",
  "channel_id": "demo-hr-channel-id",
  "location": null,
  "force_reindex": true
}
```

**Response 200:**

```json
{
  "status": "ok",
  "indexed_documents": 2,
  "indexed_chunks": 8,
  "skipped_documents": 0,
  "errors": []
}
```

**Errors:** `401` invalid/missing token · `422` validation error

---

### POST /ai/rag/answer

**Purpose:** Retrieve location-scoped HR document chunks and generate a grounded answer.

**Auth:** Bearer token required

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | string | Yes | Correlation id |
| `user_id` | string | Yes | Calling user id |
| `conversation_id` | string | Yes | Conversation id |
| `question` | string | Yes | User question (1–5000 chars) |
| `location` | `"al"` \| `"sr"` | **Yes** | Branch filter for retrieval |
| `recent_messages` | array | No | Prior chat turns `{ role, content }` |
| `authorization_scope` | object | Yes | `{ team_id, channel_id, allowed }` |
| `response_language_hint` | string \| null | No | Language hint; defaults from `location` |

**Example (Albania):**

```json
{
  "request_id": "req-1",
  "user_id": "user-1",
  "conversation_id": "conv-1",
  "question": "Si mund të kërkoj pushime?",
  "location": "al",
  "recent_messages": [],
  "authorization_scope": {
    "team_id": "demo-team-id",
    "channel_id": "demo-hr-channel-id",
    "allowed": true
  }
}
```

**Response 200:**

```json
{
  "status": "ANSWERED",
  "language": "sq",
  "answer": "...",
  "clarification_question": null,
  "sources": [
    {
      "documentId": "...",
      "title": "albania-leave-policy.txt",
      "page": null,
      "section": null,
      "sourceUrl": null,
      "modifiedAt": "...",
      "confidence": 0.82,
      "location": "al"
    }
  ]
}
```

**Status values:** `ANSWERED` · `NOT_FOUND` · `ACCESS_DENIED` · `ERROR`

**Errors:** `401` invalid/missing token · `422` validation error (e.g. missing `location`)

---

### POST /ai/test/ingest/sync

**Purpose:** Same as `POST /ai/ingest/sync` without authentication.

**Auth:** None (only when `TEST_MODE=true`, otherwise `404`)

**Request / response:** Identical to `/ai/ingest/sync`

---

### POST /ai/test/rag/answer

**Purpose:** Same as `POST /ai/rag/answer` without authentication.

**Auth:** None (only when `TEST_MODE=true`, otherwise `404`)

**Request / response:** Identical to `/ai/rag/answer` (including required `location`)

---

## Typical workflow

1. Place PDFs/DOCX/TXT/MD in `data/hr-docs/al/` and/or `data/hr-docs/sr/`
2. `POST /ai/test/ingest/sync` (or `/ai/ingest/sync`) with `force_reindex: true`
3. `POST /ai/test/rag/answer` with `"location": "al"` or `"location": "sr"`

After changing folder layout or embedding model, delete `./.chroma` and re-ingest.
