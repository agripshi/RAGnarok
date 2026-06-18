from fastapi import APIRouter, Depends

from app.core.security import require_internal_token
from app.schemas.ingest import IngestRequest, IngestResponse
from app.services.ingestion_service import IngestionService

router = APIRouter()
_service = IngestionService()


@router.post("/ingest/sync", response_model=IngestResponse)
async def ingest_sync(
    request: IngestRequest,
    _: None = Depends(require_internal_token),
) -> IngestResponse:
    return await _service.sync_documents(request)
