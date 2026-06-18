from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.api.router import ai_router
from app.core.config import settings
from app.schemas.ingest import IngestRequest
from app.services.ingestion_service import IngestionService


@asynccontextmanager
async def lifespan(_: FastAPI):
    docs_path = Path(settings.hr_docs_local_dir)
    if not docs_path.is_absolute():
        docs_path = (Path(__file__).resolve().parents[2] / settings.hr_docs_local_dir).resolve()
    if docs_path.exists():
        await IngestionService().sync_documents(
            IngestRequest(
                source_path=str(docs_path),
                team_id=settings.default_team_id,
                channel_id=settings.default_channel_id,
                force_reindex=True,
            )
        )
    yield


app = FastAPI(title="RAGnarok AI Backend", version="0.3.0", lifespan=lifespan)
app.include_router(ai_router, prefix="/ai")
