# RAGnarok HR Assistant

> Multilingual HR chatbot for Microsoft Teams — grounded answers in English, Serbian, and Albanian from private HR documents.

---

## What is RAGnarok?

RAGnarok is an internal HR assistant embedded directly in Microsoft Teams. Employees ask HR questions in their language (English, Albanian, or Serbian) and receive answers grounded **only** in the official HR documents they are authorised to access. It never invents answers — if the information is not in the documents, it says so and directs the employee to HR.

---

## How It Works — Architecture Overview

```
Microsoft Teams
      │
      ▼
┌─────────────────────────┐
│  Frontend (React/Vite)  │  ← Teams Tab (sideloaded app)
│  apps/web  :5173        │    Fluent UI dark theme, Engineering branding
└────────────┬────────────┘
             │ REST /api/*
             ▼
┌─────────────────────────┐
│  Backend API (FastAPI)  │  ← Auth, conversation storage, access control
│  apps/api  :8000        │    SQLite (local) / PostgreSQL (prod)
└────────────┬────────────┘
             │ REST /ai/rag/answer
             ▼
┌─────────────────────────┐
│  AI Backend (FastAPI)   │  ← RAG pipeline: embed → retrieve → generate
│  apps/ai   :8001        │    LangChain + OpenAI + Chroma vector DB
└─────────────────────────┘
             ▲
             │ reads
┌─────────────────────────┐
│  HR Documents           │
│  data/hr-docs/al/       │  Albanian branch PDFs
│  data/hr-docs/sr/       │  Serbian branch PDFs
└─────────────────────────┘
```

### Request Flow (step by step)

1. **Employee types a question** in Teams (any language).
2. **Frontend** sends `POST /api/chat` with the message and Teams context.
3. **Backend API** authenticates the user (dev token locally, Entra JWT in production) and checks access rights against the Engineering Albania Teams channel.
4. **Backend API** calls `POST /ai/rag/answer` with the question, conversation history, and `location: "al"` or `"sr"` (branch filter).
5. **AI Backend** embeds the question using `text-embedding-3-small` (OpenAI).
6. **AI Backend** retrieves the top-K most relevant chunks from Chroma, filtered to the correct branch (`al` or `sr`).
7. **AI Backend** detects the question language and calls `gpt-4o-mini` with a strict system prompt: *"Answer only from the provided context. If the answer is not in the documents, say so."*
8. **AI Backend** returns the answer, detected language, and source references (document title, page, confidence).
9. **Backend API** stores the full exchange in SQLite and returns the response.
10. **Frontend** renders the answer in the chat bubble with source cards below each assistant message.

---

## Key Mechanisms Implemented

### 🔍 RAG Pipeline (Retrieval-Augmented Generation)
- Documents chunked at 900 chars / 120 overlap using LangChain's `RecursiveCharacterTextSplitter`
- Each chunk tagged with `location` (`al` / `sr`), `team_id`, `channel_id`
- Retrieval is **location-scoped** — Albanian employees only get Albanian HR chunks
- Top-6 chunks retrieved, similarity threshold 0.15, sent as context to the LLM
- LLM instructed to answer only from retrieved context → no hallucination

### 🌍 Multilingual Support
- **English**, **Serbian**, **Albanian** supported
- Language auto-detected per message using `langdetect`
- LLM responds in the same language the question was asked
- Serbian preserves Latin or Cyrillic script based on user input

### 📄 Document Ingestion
- Supports PDF, DOCX, TXT, MD files
- `PyPDFLoader` for PDFs → text extraction per page
- Incremental ingest: file hash checked, unchanged files skipped
- Re-ingest forced with `force_reindex: true`
- Documents stored in `data/hr-docs/al/` and `data/hr-docs/sr/`

### 🔐 Access Control (v1)
- Backend validates user against an email allowlist (`authorized_user_ids`)
- `authorization_scope` sent with every AI request (`team_id`, `channel_id`, `allowed`)
- Dev mode: `Bearer dev-token` bypasses auth for local testing
- Every chat message scoped to a conversation owned by the authenticated user

### 💬 Conversation Management
- Full conversation history stored in SQLite
- Conversations listed in the toolbar sidebar
- Previous conversations resumable
- Each message stored with language, status, and source references

### 📎 Source Cards
- Every assistant answer includes source cards rendered below the message
- Cards show: document title, section, page number, confidence score
- When document URL available (future): deep-link to file in Teams/SharePoint

### 🎨 Teams Integration
- Fluent UI v9 dark theme with Engineering brand colours
- Teams SDK initialised — app aware it's running inside Teams
- App package: `color.png` (192×192) + `outline.png` (32×32) + `manifest.json`
- Sideloaded via Teams Developer Portal or manual zip upload

### 👍 Feedback System
- Thumbs up / down on every assistant response
- Feedback stored in DB linked to the specific message
- Foundation for quality tracking and fine-tuning

---

## Running Locally (Ubuntu/Linux)

```bash
# 1. AI Backend
cd apps/ai && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # set LLM_API_KEY and LLM_MOCK_ENABLED=false
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001

# 2. Backend API
cd apps/api && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000

# 3. Frontend
cd apps/web && npm install && npm run dev

# 4. Tunnel (for Teams — requires HTTPS public URL)
npx tunnelmole 5173
# → update apps/web/appPackage/manifest.json with new URL
# → rebuild zip: cd apps/web/appPackage && zip -j ../../../ragnarok-teams.zip manifest.json color.png outline.png
# → re-upload zip in Teams

# 5. Ingest documents
curl -X POST http://127.0.0.1:8001/ai/ingest/sync \
  -H "Authorization: Bearer dev-internal-token" \
  -H "Content-Type: application/json" \
  -d '{"team_id":"1531e68a-4716-43aa-bc3b-41b11451cbbb","channel_id":"19:11b56c75623d48ac828e2797373cacae@thread.tacv2","force_reindex":true}'
```

### Health Checks

| Service | URL |
|---|---|
| AI Backend | http://127.0.0.1:8001/ai/health |
| Backend API | http://127.0.0.1:8000/api/health |
| Frontend | http://localhost:5173 |

### Non-secret channel config

See `config/channels.env` for Engineering Albania Teams channel IDs.

---

## Teams Channel Configuration (v1)

| Setting | Value |
|---|---|
| Team | Engineering Albania |
| Team ID | `1531e68a-4716-43aa-bc3b-41b11451cbbb` |
| Channel | Documents - Engineering Albania |
| Channel ID | `19:11b56c75623d48ac828e2797373cacae@thread.tacv2` |
| Tenant | `f2d7d6c5-1bee-41ff-9e79-b372a5cce71d` |

> ⚠️ Channel IDs are **not secrets** — they are public Teams identifiers. Secrets (`TENANT_ID`, `BACKEND_CLIENT_ID`, `BACKEND_CLIENT_SECRET`) are required only for Graph API integration (v2).

---

## Known v1 Limitations

| Limitation | Impact |
|---|---|
| Scanned PDFs (image-only) | Text cannot be extracted → those documents return "not found" |
| Tunnel URL changes on restart | Must re-upload Teams zip after every tunnelmole restart |
| Dev token auth only | No real Entra JWT validation — any user can access in dev mode |
| Local filesystem documents | App reads from `data/hr-docs/` not live from Teams/SharePoint |
| SQLite database | Not suitable for multi-user production load |
| No HTTPS in dev | Vite runs HTTP; tunnelmole provides HTTPS termination |

---

## v2 Roadmap — Production Improvements

### 🔐 Authentication & Authorisation
- **Entra ID (Azure AD) JWT validation** — validate Teams SSO tokens server-side
- **Microsoft Graph channel membership check** — verify user is actually a member of the Teams channel before answering, not just an email allowlist
- **OBO (On-Behalf-Of) flow** — backend calls Graph API on behalf of the authenticated user

### 📂 Live Document Sync from Teams/SharePoint
- **Graph API integration** — `GET /sites/{site}/drives/{drive}/items` to list and download files directly from the Teams channel's SharePoint library
- **Delta sync** — poll for changed files using SharePoint delta tokens, re-index only modified documents
- No more manual file uploads to `data/hr-docs/`

### 🗄️ Infrastructure
- **PostgreSQL** instead of SQLite for conversation and feedback storage
- **Qdrant** (or hosted Chroma) as persistent vector store — survives restarts, scales horizontally
- **Azure App Service** deployment for API + AI backends (`scripts/deploy-azure.sh` already written)
- **Azure Static Web Apps** for frontend (`apps/web/public/staticwebapp.config.json` already written)
- **Stable HTTPS URL** — no more tunnelmole; Teams manifest points to Azure domain

### 🤖 AI Quality
- **Scanned PDF OCR** — integrate `pytesseract` or OpenAI vision to extract text from image-only PDFs
- **Reranker** — add cross-encoder reranking step after retrieval for higher precision
- **Hybrid search** — combine dense (semantic) + sparse (BM25) retrieval
- **Streaming responses** — stream LLM tokens to frontend for faster perceived response
- **Conversation memory** — include more context turns in RAG prompt for follow-up questions

### 🌍 Language & UX
- **Serbian Cyrillic/Latin auto-detection** — preserve script based on user input
- **Clarification flow UI** — when AI returns `NEEDS_CLARIFICATION`, show a prompt card instead of plain text
- **Serbian branch documents** — full document set for Serbia office

### 📊 Observability
- **LangSmith / LangFuse tracing** — log every RAG chain step, retrieval quality, LLM latency
- **Feedback analytics dashboard** — aggregate thumbs up/down by document and question type
- **Admin ingest UI** — trigger re-ingest from the Teams app without needing curl

---

## Documentation

| File | Contents |
|---|---|
| `docs/DEMO.md` | 10-minute hackathon demo script |
| `docs/TEAMS_DEPLOYMENT_CHECKLIST.md` | Local sideload + Azure production path |
| `docs/TEAMS_INTEGRATION_VERIFICATION_REPORT.md` | Teams channel integration audit |
| `docs/TEAMS_CHANNEL_DOCUMENT_ACCESS_VERIFICATION.md` | Graph/SharePoint gap analysis for v2 |
| `docs/RAGnarok_Technical_Architecture_Spec.md` | Full technical architecture |
| `docs/RAGnarok_Business_Foundational_Spec.md` | Business requirements and user stories |
| `docs/RAGnarok_AI_LangChain_LangGraph_Implementation_Technical_Doc.md` | AI pipeline design |
| `apps/ai/API_CONTRACTS.md` | AI backend endpoint reference |
| `config/channels.env` | Non-secret Teams channel identifiers |

## Agents

Specialized Copilot agents in `agents/` — one per implementation layer (frontend, backend, AI, test, code-review).

