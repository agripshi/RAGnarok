from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings


def get_embeddings() -> Embeddings:
    if settings.embedding_provider != "openai":
        raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")

    api_key = settings.embedding_api_key or settings.llm_api_key
    if not api_key:
        if settings.vector_db == "memory":
            from langchain_core.embeddings import FakeEmbeddings

            return FakeEmbeddings(size=settings.embedding_dimensions)
        raise ValueError(
            "OpenAI embeddings require EMBEDDING_API_KEY or LLM_API_KEY to be set."
        )

    kwargs: dict = {
        "model": settings.embedding_model,
        "api_key": api_key,
    }
    if settings.embedding_model.startswith("text-embedding-3"):
        kwargs["dimensions"] = settings.embedding_dimensions

    return OpenAIEmbeddings(**kwargs)
