from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "ragnarok-ai-backend",
        "vectorDb": settings.vector_db,
        "llmMode": "mock" if settings.llm_mock_enabled or not settings.llm_api_key else "cloud",
    }
