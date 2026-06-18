# RAGnarok HR Assistant - Backend and Relational DB Implementation Technical Doc

**Audience:** Cursor / backend developer  
**Scope:** Backend API + relational database only  
**Backend stack:** Python + FastAPI + SQLAlchemy + Alembic + PostgreSQL  
**External dependencies:** Microsoft Teams SSO token, Microsoft Graph, AI Backend HTTP API  
**Version:** 1.0

---

## 1. Goal of This Document

Build the Backend API and PostgreSQL relational database for the RAGnarok HR Assistant.

The Backend API is the trusted orchestration layer between the Teams frontend, the relational DB, Microsoft identity/access checks, and the AI backend.

The Backend must:

1. Validate authenticated Teams users.
2. Verify that the user is allowed to access the private HR Teams channel.
3. Store users, conversations, messages, sources, feedback, documents, and audit logs.
4. Receive chat requests from the frontend.
5. Call the AI backend with an authorization scope.
6. Return structured answers to the frontend.
7. Trigger ingestion/sync by calling the AI backend.
8. Never generate HR answers directly.
9. Never expose HR document metadata to unauthorized users.

---

## 2. Component Boundaries

```text
React Frontend
    |
    | HTTPS REST + Bearer Teams token
    v
Backend API - FastAPI
    |
    +--> PostgreSQL - relational metadata and chat history
    |
    +--> Microsoft Graph - private channel access validation
    |
    +--> AI Backend - LangChain / LangGraph RAG service
```

### Backend owns

- API contracts consumed by frontend.
- Authentication validation.
- Authorization decision.
- Relational DB schema.
- Conversation persistence.
- Feedback persistence.
- Audit logs.
- AI backend orchestration.

### Backend does not own

- React UI rendering.
- Vector search internals.
- LangChain/LangGraph graph logic.
- Embedding generation.
- LLM prompt execution.

---

## 3. Tech Stack

| Area | Technology |
|---|---|
| Runtime | Python 3.11+ |
| Web framework | FastAPI |
| ASGI server | Uvicorn |
| DB | PostgreSQL 16+ |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| HTTP client | httpx |
| Auth/JWT | python-jose or PyJWT + cryptography |
| Microsoft OBO | MSAL optional for production Graph access |
| Testing | pytest + httpx AsyncClient |
| Formatting | ruff + black optional |

---

## 4. Service Ports and URLs

Local defaults:

```text
Frontend:       http://localhost:5173
Backend API:    http://localhost:8000
AI Backend:     http://localhost:8001
PostgreSQL:     localhost:5432
Qdrant:         localhost:6333
```

Frontend calls only Backend API.  
Backend calls AI Backend.  
Backend calls PostgreSQL.  
Backend calls Microsoft Graph for access validation.

---

## 5. Project Setup Commands

Create the backend under `apps/api`.

```bash
mkdir -p apps/api
cd apps/api
python -m venv .venv
source .venv/bin/activate  # Windows Git Bash: source .venv/Scripts/activate
pip install fastapi uvicorn[standard] sqlalchemy alembic psycopg[binary] pydantic-settings httpx python-jose[cryptography] msal pytest pytest-asyncio
pip freeze > requirements.txt
```

Recommended run command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 6. Environment Variables

Create `apps/api/.env.example`:

```env
APP_ENV=local
API_HOST=0.0.0.0
API_PORT=8000

DATABASE_URL=postgresql+psycopg://ragnarok:ragnarok@localhost:5432/ragnarok_hr

FRONTEND_ORIGINS=http://localhost:5173,https://localhost:53000

# Microsoft Entra / Teams
TENANT_ID=
BACKEND_CLIENT_ID=
BACKEND_CLIENT_SECRET=
EXPECTED_TOKEN_AUDIENCE=
TEAM_ID=
HR_PRIVATE_CHANNEL_ID=

# Microsoft Graph
GRAPH_BASE_URL=https://graph.microsoft.com/v1.0
GRAPH_SCOPES=https://graph.microsoft.com/.default

# AI Backend
AI_BACKEND_URL=http://localhost:8001
AI_BACKEND_INTERNAL_TOKEN=dev-internal-token

# MVP auth fallback
DEV_AUTH_ENABLED=true
DEV_AUTH_USER_ID=dev-user-001
DEV_AUTH_EMAIL=demo.user@company.com
AUTHORIZED_EMAILS=demo.user@company.com,etienhaskocelaj@gmail.com
AUTHORIZED_USER_IDS=dev-user-001

# Access check cache
ACCESS_CACHE_TTL_SECONDS=300

# Admin
ADMIN_EMAILS=etienhaskocelaj@gmail.com
```

Rules:

- `BACKEND_CLIENT_SECRET` must never be exposed to frontend.
- `AI_BACKEND_INTERNAL_TOKEN` is a backend-to-AI service token and must never be exposed to frontend.
- `DEV_AUTH_ENABLED=true` is only for local demo.

---

## 7. Recommended Backend File Structure

```text
apps/api/
  requirements.txt
  alembic.ini
  .env.example
  app/
    main.py
    core/
      config.py
      errors.py
      logging.py
      security.py
    db/
      base.py
      session.py
      models.py
      repositories/
        users.py
        conversations.py
        messages.py
        documents.py
        feedback.py
        access_cache.py
    schemas/
      auth.py
      chat.py
      conversation.py
      feedback.py
      documents.py
      common.py
    api/
      router.py
      routes/
        health.py
        me.py
        chat.py
        conversations.py
        feedback.py
        admin_ingest.py
    services/
      auth_service.py
      graph_access_service.py
      access_guard.py
      ai_client.py
      chat_service.py
      ingestion_orchestrator.py
      audit_service.py
  alembic/
    env.py
    versions/
```

---

## 8. PostgreSQL Schema

Use UUID primary keys. Use timezone-aware timestamps where possible.

### 8.1 SQL DDL Foundation

Create the initial Alembic migration with the following logical schema.

```sql
CREATE TABLE app_user (
    id UUID PRIMARY KEY,
    entra_user_id TEXT UNIQUE NOT NULL,
    email TEXT,
    display_name TEXT,
    tenant_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE conversation (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES app_user(id),
    title TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE message (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    language TEXT,
    status TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE document (
    id UUID PRIMARY KEY,
    source_provider TEXT NOT NULL,
    team_id TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    title TEXT NOT NULL,
    source_url TEXT,
    latest_version_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE document_version (
    id UUID PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES document(id) ON DELETE CASCADE,
    modified_at TIMESTAMPTZ,
    content_hash TEXT NOT NULL,
    language TEXT,
    office TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(document_id, content_hash)
);

ALTER TABLE document
ADD CONSTRAINT fk_document_latest_version
FOREIGN KEY (latest_version_id) REFERENCES document_version(id);

CREATE TABLE document_chunk (
    id UUID PRIMARY KEY,
    document_version_id UUID NOT NULL REFERENCES document_version(id) ON DELETE CASCADE,
    vector_point_id TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    page INTEGER,
    section TEXT,
    text_preview TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE answer_source (
    id UUID PRIMARY KEY,
    message_id UUID NOT NULL REFERENCES message(id) ON DELETE CASCADE,
    document_id UUID,
    document_version_id UUID,
    chunk_id UUID,
    title TEXT NOT NULL,
    page INTEGER,
    section TEXT,
    source_url TEXT,
    score DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE feedback (
    id UUID PRIMARY KEY,
    message_id UUID NOT NULL REFERENCES message(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES app_user(id),
    rating TEXT NOT NULL CHECK (rating IN ('helpful', 'not_helpful')),
    comment TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE access_check_cache (
    id UUID PRIMARY KEY,
    entra_user_id TEXT NOT NULL,
    team_id TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    allowed BOOLEAN NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(entra_user_id, team_id, channel_id)
);

CREATE TABLE audit_log (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES app_user(id),
    action TEXT NOT NULL,
    status TEXT NOT NULL,
    metadata_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 8.2 Indexes

Add indexes:

```sql
CREATE INDEX idx_conversation_user_id ON conversation(user_id);
CREATE INDEX idx_message_conversation_id ON message(conversation_id);
CREATE INDEX idx_document_source ON document(team_id, channel_id);
CREATE INDEX idx_document_version_active ON document_version(document_id, is_active);
CREATE INDEX idx_answer_source_message_id ON answer_source(message_id);
CREATE INDEX idx_access_cache_lookup ON access_check_cache(entra_user_id, team_id, channel_id, expires_at);
CREATE INDEX idx_audit_log_user_created ON audit_log(user_id, created_at);
```

---

## 9. SQLAlchemy Models

Create SQLAlchemy models matching the schema in `app/db/models.py`.

Rules:

- Use `Mapped[]` annotations.
- Use `uuid.uuid4` for UUID IDs.
- Use relationships for `User -> Conversation -> Message -> AnswerSource`.
- Keep model logic minimal.
- Business logic belongs in services.

Model names:

```text
AppUser
Conversation
Message
Document
DocumentVersion
DocumentChunk
AnswerSource
Feedback
AccessCheckCache
AuditLog
```

---

## 10. Pydantic Schemas

Create `app/schemas/chat.py`.

```python
from pydantic import BaseModel, Field
from typing import Literal

AnswerStatus = Literal['ANSWERED', 'NEEDS_CLARIFICATION', 'NOT_FOUND', 'ACCESS_DENIED', 'ERROR']
SupportedLanguage = Literal['sq', 'it', 'sr', 'en', 'unknown']

class TeamsContextPayload(BaseModel):
    teamId: str | None = None
    channelId: str | None = None
    userId: str | None = None
    locale: str | None = None
    tenantId: str | None = None

class ChatRequest(BaseModel):
    conversationId: str | None = None
    message: str = Field(min_length=1, max_length=5000)
    teamsContext: TeamsContextPayload

class SourceCardDto(BaseModel):
    documentId: str | None = None
    title: str
    page: int | None = None
    section: str | None = None
    sourceUrl: str | None = None
    modifiedAt: str | None = None
    confidence: float | None = None

class ChatResponse(BaseModel):
    conversationId: str
    messageId: str
    status: AnswerStatus
    language: SupportedLanguage
    answer: str
    clarificationQuestion: str | None = None
    sources: list[SourceCardDto] = []
```

Create `app/schemas/feedback.py`.

```python
class FeedbackRequest(BaseModel):
    messageId: str
    rating: Literal['helpful', 'not_helpful']
    comment: str | None = None
```

---

## 11. Authentication Service

Create `app/services/auth_service.py`.

Responsibilities:

1. Extract bearer token.
2. In local dev mode, accept `dev-token` and return a fake user.
3. In Teams mode, validate JWT against Microsoft Entra JWKS.
4. Return an `AuthenticatedUser` object.

`AuthenticatedUser` fields:

```python
class AuthenticatedUser(BaseModel):
    entra_user_id: str
    email: str | None = None
    display_name: str | None = None
    tenant_id: str | None = None
    raw_token: str
```

JWT validation rules:

- Validate signature using tenant JWKS.
- Validate expiration.
- Validate issuer.
- Validate audience.
- Extract `oid` as `entra_user_id`.
- Extract `preferred_username` or `upn` as email if available.
- Extract `name` as display name if available.

Local dev fallback:

```text
Authorization: Bearer dev-token
```

Only enable when `DEV_AUTH_ENABLED=true`.

---

## 12. Private Channel Access Guard

Create `app/services/access_guard.py`.

Public method:

```python
async def assert_user_can_access_hr_channel(user: AuthenticatedUser) -> None:
    ...
```

Flow:

1. Check `access_check_cache` for `(entra_user_id, TEAM_ID, HR_PRIVATE_CHANNEL_ID)`.
2. If valid cached positive result exists, allow.
3. If local dev enabled, check `AUTHORIZED_EMAILS` or `AUTHORIZED_USER_IDS`.
4. If production mode, call `GraphAccessService`.
5. Store result in cache with TTL.
6. If not allowed, raise `AccessDeniedError`.

### 12.1 GraphAccessService

Create `app/services/graph_access_service.py`.

Production target logic:

1. Use On-Behalf-Of flow to exchange the backend token for a Microsoft Graph delegated token.
2. Call Graph to verify that the user can see or is a member of the configured private channel.
3. Preferred check:
   - `GET /teams/{TEAM_ID}/channels/{HR_PRIVATE_CHANNEL_ID}/members`
   - Match user by Entra object ID or email.
4. Alternative check:
   - Attempt to access the private channel-backed SharePoint folder with user-delegated token.
   - If Graph returns `403`, deny.

MVP fallback:

- Use `AUTHORIZED_EMAILS` / `AUTHORIZED_USER_IDS` env list.
- Keep method interface identical so Graph can replace it later.

Important:

- Access guard must run on every chat request.
- Cache only for a short TTL, e.g. 300 seconds.
- Deny on Graph error unless `APP_ENV=local` and fallback is explicitly enabled.

---

## 13. AI Backend Client

Create `app/services/ai_client.py`.

Backend calls AI backend by HTTP. It does not import LangChain code.

### 13.1 AI Answer Request

```python
class AiAnswerRequest(BaseModel):
    request_id: str
    user_id: str
    conversation_id: str
    question: str
    recent_messages: list[dict]
    authorization_scope: dict
    response_language_hint: str | None = None
```

`authorization_scope` must include:

```json
{
  "team_id": "configured-team-id",
  "channel_id": "private-hr-channel-id",
  "allowed": true
}
```

### 13.2 AI Answer Response

```python
class AiAnswerResponse(BaseModel):
    status: Literal['ANSWERED', 'NEEDS_CLARIFICATION', 'NOT_FOUND', 'ACCESS_DENIED', 'ERROR']
    language: str
    answer: str
    clarification_question: str | None = None
    sources: list[SourceCardDto] = []
```

### 13.3 HTTP Call

Endpoint:

```text
POST {AI_BACKEND_URL}/ai/rag/answer
Authorization: Bearer {AI_BACKEND_INTERNAL_TOKEN}
```

Rules:

- Set timeout to 60 seconds for MVP.
- Convert AI errors into controlled backend responses.
- Never send raw frontend bearer token to AI backend.
- Send only the backend-decided authorization scope.

---

## 14. Chat Service

Create `app/services/chat_service.py`.

Method:

```python
async def handle_chat(request: ChatRequest, user: AuthenticatedUser) -> ChatResponse:
    ...
```

Flow:

1. Upsert `app_user` by `entra_user_id`.
2. Run access guard.
3. Create conversation if `conversationId` is null.
4. Verify conversation belongs to the current user if provided.
5. Save user message.
6. Load recent conversation messages, e.g. last 6 messages.
7. Build `AiAnswerRequest`.
8. Call AI backend.
9. Save assistant message with returned status/language/content.
10. Save answer sources.
11. Return `ChatResponse` to frontend.

Important:

- If access guard fails, do not call AI backend.
- If AI returns `ACCESS_DENIED`, still treat it as denial and do not show sources.
- If AI returns `NOT_FOUND`, save assistant response and no sources.

---

## 15. API Routes

## 15.1 Health

`GET /api/health`

Response:

```json
{
  "status": "ok",
  "service": "ragnarok-backend"
}
```

## 15.2 Me

`GET /api/me`

Requires auth.

Flow:

1. Validate token.
2. Upsert user.
3. Run access check.
4. Return profile and access status.

Response:

```json
{
  "userId": "uuid",
  "email": "demo.user@company.com",
  "displayName": "Demo User",
  "hasHrAccess": true
}
```

## 15.3 Chat

`POST /api/chat`

Requires auth.

Consumes `ChatRequest`. Returns `ChatResponse`.

## 15.4 Conversations

`GET /api/conversations`

Requires auth. Returns only conversations for current user.

`GET /api/conversations/{conversation_id}`

Requires auth. Verify owner.

## 15.5 Feedback

`POST /api/feedback`

Requires auth. Verify message belongs to current user's conversation.

## 15.6 Admin Ingestion

`POST /api/admin/ingest/sync`

Requires admin authorization.

Flow:

1. Validate user.
2. Check `email in ADMIN_EMAILS`.
3. Call AI backend endpoint `/ai/ingest/sync`.
4. Store returned document metadata if provided.
5. Return ingestion summary.

---

## 16. Error Handling

Create custom exceptions in `app/core/errors.py`:

```text
AuthenticationError -> 401
AccessDeniedError -> 403
ConversationNotFoundError -> 404
AiBackendError -> 502
ValidationError -> 400
UnhandledError -> 500
```

Response shape:

```json
{
  "error": {
    "code": "ACCESS_DENIED",
    "message": "Access restricted to members of the private HR Teams channel."
  }
}
```

Rules:

- Do not include stack traces in API responses.
- Do not include Graph token details.
- Do not include document names in access denied responses.
- Log internal details server-side.

---

## 17. CORS

Allow frontend origins from `FRONTEND_ORIGINS`.

Example:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

---

## 18. Docker Compose

At repo root, create `infra/docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:16
    container_name: ragnarok-postgres
    environment:
      POSTGRES_USER: ragnarok
      POSTGRES_PASSWORD: ragnarok
      POSTGRES_DB: ragnarok_hr
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  qdrant:
    image: qdrant/qdrant:latest
    container_name: ragnarok-qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  postgres_data:
  qdrant_data:
```

Backend uses Postgres. AI backend uses Qdrant.

---

## 19. Implementation Steps for Cursor

### Step 1 - Create FastAPI project

Generate `apps/api/app/main.py`, config, router, and health route.

### Step 2 - Add settings

Use `pydantic-settings` in `app/core/config.py`.

### Step 3 - Add DB session

Create SQLAlchemy engine and session dependency.

### Step 4 - Add models

Implement all models listed in this document.

### Step 5 - Add Alembic

Initialize Alembic and create initial migration.

Commands:

```bash
alembic init alembic
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

### Step 6 - Add auth service

Implement dev-token mode first. Keep JWT validation structure ready.

### Step 7 - Add access guard

Implement allowlist fallback first. Keep Graph service interface ready.

### Step 8 - Add AI client

Implement HTTP client for `/ai/rag/answer`.

### Step 9 - Add chat service

Implement full chat orchestration and persistence.

### Step 10 - Add routes

Implement `/api/chat`, `/api/me`, `/api/conversations`, `/api/feedback`, and `/api/admin/ingest/sync`.

### Step 11 - Add error handlers

Return consistent JSON errors.

### Step 12 - Add tests

Minimum tests:

- health endpoint.
- chat with dev token and authorized email.
- chat unauthorized returns 403 and does not call AI client.
- chat saves user and assistant messages.
- feedback stores feedback.

---

## 20. Backend Acceptance Criteria

The Backend + DB implementation is complete when:

1. `uvicorn app.main:app --reload` starts successfully.
2. Alembic migration creates all tables.
3. `GET /api/health` returns OK.
4. `POST /api/chat` requires bearer token.
5. Unauthorized users receive 403.
6. Authorized users can create a conversation and message.
7. Backend calls AI backend with `authorization_scope`.
8. Backend stores user message, assistant message, and answer sources.
9. Feedback endpoint stores user feedback.
10. Admin ingestion endpoint calls AI backend.
11. Frontend never needs to know AI backend URL.
12. No HR answer is returned if access guard fails.
13. No document metadata is returned to unauthorized users.

---

## 21. Cursor Final Instruction

When using this document in Cursor, generate only Backend API and relational database code under `apps/api`. Do not implement React UI. Do not implement LangChain/LangGraph internals. The Backend must communicate with the AI backend only through the HTTP contracts defined above.
