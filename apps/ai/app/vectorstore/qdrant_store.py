from app.core.config import settings
from app.vectorstore.base import ChunkRecord, RetrievedChunk
from app.vectorstore.chroma_store import ChromaVectorStore


class QdrantVectorStore(ChromaVectorStore):
    """Fallback to Chroma when Qdrant is unavailable in local dev."""

    def __init__(self) -> None:
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.http.models import Distance, VectorParams

            self._client = QdrantClient(url=settings.qdrant_url)
            if not self._client.collection_exists(settings.qdrant_collection):
                self._client.create_collection(
                    collection_name=settings.qdrant_collection,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                )
            self._use_qdrant = True
        except Exception:
            super().__init__()
            self._use_qdrant = False

    def upsert_chunks(self, chunks: list[ChunkRecord]) -> None:
        if not self._use_qdrant:
            return super().upsert_chunks(chunks)
        # Qdrant path deferred — Chroma handles local MVP
        return super().upsert_chunks(chunks)

    def search(self, query: str, team_id: str, channel_id: str, top_k: int) -> list[RetrievedChunk]:
        if not self._use_qdrant:
            return super().search(query, team_id, channel_id, top_k)
        return super().search(query, team_id, channel_id, top_k)

    def count(self) -> int:
        if not self._use_qdrant:
            return super().count()
        return super().count()
