# RAGnarok HR Assistant

Multilingual HR chatbot for Microsoft Teams — grounded answers from private HR documents (English, Serbian, Albanian).

## Architecture

```text
Teams Frontend (apps/web) → Backend API (apps/api) → AI Backend (apps/ai)
                                ↓                           ↓
                      SQLite (local) / PostgreSQL          Memory / Chroma / Qdrant
```

## Prerequisites

- Node.js 20+
- Python 3.11+
- Docker Desktop (optional — for PostgreSQL + Qdrant in production)

## Quick Start

**One command (Windows):** `.\scripts\start-dev.ps1` — opens AI, API, and frontend in separate terminals.

Or start manually:

### 1. AI Backend (port 8001) — start first

Auto-ingests `data/hr-docs/` on startup.

```bash
cd apps/ai
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

### 2. Backend API (port 8000)

Uses SQLite by default (`ragnarok_local.db`) — no Docker required.

```bash
cd apps/api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Frontend (port 5173)

```bash
cd apps/web
npm install
copy .env.example .env.local
npm run dev
```

Open http://localhost:5173 — use dev token auth automatically in browser.

## LLM Configuration

Mock mode is **on** by default. To use a cloud model:

```env
# apps/ai/.env
LLM_API_KEY=sk-...
LLM_MOCK_ENABLED=false
```

## Health Checks

| Service | URL |
|---|---|
| Backend | http://127.0.0.1:8000/api/health |
| AI | http://127.0.0.1:8001/ai/health |
| Frontend | http://localhost:5173 |

## Sprint Progress

| Sprint | Focus | Progress |
|---|---|---|
| Sprint 0 | Foundation & scaffolding | **100%** |
| Sprint 1 | UI + API + DB skeleton | **100%** |
| Sprint 2 | AI ingestion & RAG (mock LLM) | **100%** |
| Sprint 3 | E2E integration (FE→BE→AI) | **100%** |
| Sprint 4 | Feedback, access guard, admin ingest | **100%** |
| Sprint 5 | Tests & demo freeze | **100%** |

**Overall: 100%** (MVP demo-ready)

## Documentation

- `docs/DEMO.md` — 10-minute hackathon demo script
- `docs/TEAMS_DEPLOYMENT_CHECKLIST.md` — local sideload + Azure production path
- `docs/RAGnarok_Technical_Architecture_Spec.md`
- `docs/RAGnarok_Frontend_Implementation_Technical_Doc.md`
- `docs/RAGnarok_Backend_DB_Implementation_Technical_Doc.md`
- `docs/RAGnarok_AI_LangChain_LangGraph_Implementation_Technical_Doc.md`

## Agents

Specialized Cursor agents in `agents/` — one per implementation layer.
