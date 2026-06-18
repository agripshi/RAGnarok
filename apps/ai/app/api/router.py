from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.ingest import router as ingest_router
from app.api.routes.ingest_test import router as ingest_test_router
from app.api.routes.rag import router as rag_router
from app.api.routes.rag_test import router as rag_test_router
from app.core.config import settings

ai_router = APIRouter()
ai_router.include_router(health_router, tags=["health"])
ai_router.include_router(rag_router, tags=["rag"])
ai_router.include_router(ingest_router, tags=["ingest"])

if settings.test_mode:
    ai_router.include_router(ingest_test_router, prefix="/test", tags=["ingest-test"])
    ai_router.include_router(rag_test_router, prefix="/test", tags=["rag-test"])
