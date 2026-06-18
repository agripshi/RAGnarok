from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.rag import router as rag_router
from app.api.routes.ingest import router as ingest_router

ai_router = APIRouter()
ai_router.include_router(health_router, tags=["health"])
ai_router.include_router(rag_router, tags=["rag"])
ai_router.include_router(ingest_router, tags=["ingest"])
