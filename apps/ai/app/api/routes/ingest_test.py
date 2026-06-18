from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.schemas.ingest import IngestRequest, IngestResponse
from app.services.ingestion_service import IngestionService

router = APIRouter()
_service = IngestionService()


@router.post("/ingest/sync", response_model=IngestResponse)
async def ingest_sync_test(request: IngestRequest) -> IngestResponse:
    if not settings.test_mode:
        raise HTTPException(status_code=404, detail="Not found")
    return await _service.sync_documents(request)
