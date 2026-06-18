from app.vectorstore.hr_store import HrVectorStore, _get_chroma_store


def get_qdrant_vector_store() -> HrVectorStore:
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.http.models import Distance, VectorParams

        from app.core.config import settings

        client = QdrantClient(url=settings.qdrant_url)
        if not client.collection_exists(settings.qdrant_collection):
            client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=VectorParams(
                    size=settings.embedding_dimensions,
                    distance=Distance.COSINE,
                ),
            )
    except Exception:
        pass

    # Qdrant LangChain integration deferred — Chroma handles local MVP.
    return HrVectorStore(_get_chroma_store())
