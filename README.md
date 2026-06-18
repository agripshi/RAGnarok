# RAGnarok HR Assistant

Multilingual HR chatbot for Microsoft Teams — grounded answers from private HR documents (Albanian, Italian, Serbian).

## Architecture

```text
Teams Frontend (apps/web) → Backend API (apps/api) → AI Backend (apps/ai)
                                ↓                           ↓
                           PostgreSQL                    Qdrant
```

## Prerequisites

- Node.js 20+
- Python 3.11+
- Docker Desktop

## Quick Start

### 1. Infrastructure

```bash
docker compose -f infra/docker-compose.yml up -d
```

### 2. Backend API (port 8000)

```bash
cd apps/api
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. AI Backend (port 8001)

```bash
cd apps/ai
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 4. Frontend (port 5173)

```bash
cd apps/web
npm install
copy .env.example .env.local
npm run dev
```

## Health Checks

| Service | URL |
|---|---|
| Backend | http://localhost:8000/api/health |
| AI | http://localhost:8001/ai/health |
| Frontend | http://localhost:5173 |

## Documentation

- `docs/RAGnarok_Business_Foundational_Spec.md`
- `docs/RAGnarok_Technical_Architecture_Spec.md`
- `docs/RAGnarok_Frontend_Implementation_Technical_Doc.md`
- `docs/RAGnarok_Backend_DB_Implementation_Technical_Doc.md`
- `docs/RAGnarok_AI_LangChain_LangGraph_Implementation_Technical_Doc.md`

## Agents

Specialized Cursor agents live in `agents/` — one per implementation layer.

## Sprint Progress

| Sprint | Focus | Status |
|---|---|---|
| Sprint 0 | Foundation & scaffolding | In progress |
| Sprint 1 | UI + API + DB skeleton | Pending |
| Sprint 2 | AI ingestion & RAG | Pending |
| Sprint 3 | E2E integration | Pending |
| Sprint 4 | Security & UX polish | Pending |
| Sprint 5 | Test & demo freeze | Pending |
