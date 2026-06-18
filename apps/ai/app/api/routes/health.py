from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str | bool]:
    has_api_key = bool(settings.llm_api_key or settings.embedding_api_key)
    return {
        "status": "ok",
        "service": "ragnarok-ai-backend",
        "testMode": settings.test_mode,
        "vectorDb": settings.vector_db,
        "embeddingProvider": settings.embedding_provider if settings.vector_db != "memory" else "none",
        "embeddingModel": settings.embedding_model if settings.vector_db != "memory" else "none",
        "llmMode": "mock" if settings.llm_mock_enabled or not settings.llm_api_key else "cloud",
        "llmModel": settings.llm_model if has_api_key and not settings.llm_mock_enabled else "mock",
    }
