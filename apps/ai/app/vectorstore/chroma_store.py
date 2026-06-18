from pathlib import Path

import chromadb

from app.core.config import settings
from app.vectorstore.base import ChunkRecord, RetrievedChunk, VectorStore


class ChromaVectorStore:
    def __init__(self) -> None:
        persist = Path(settings.chroma_persist_dir)
        persist.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(persist))
        self._collection = self._client.get_or_create_collection(
            name="hr_documents",
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_chunks(self, chunks: list[ChunkRecord]) -> None:
        if not chunks:
            return
        self._collection.upsert(
            ids=[c.chunk_id for c in chunks],
            documents=[c.text for c in chunks],
            metadatas=[
                {
                    "document_id": c.document_id,
                    "title": c.title,
                    "team_id": c.team_id,
                    "channel_id": c.channel_id,
                    "language": c.language or "",
                    "office": c.office or "",
                    "page": c.page if c.page is not None else -1,
                    "section": c.section or "",
                    "source_url": c.source_url or "",
                    "modified_at": c.modified_at or "",
                    "content_hash": c.content_hash,
                    "is_active": True,
                }
                for c in chunks
            ],
        )

    def search(self, query: str, team_id: str, channel_id: str, top_k: int) -> list[RetrievedChunk]:
        if self._collection.count() == 0:
            return []
        results = self._collection.query(
            query_texts=[query],
            n_results=min(top_k, self._collection.count()),
            where={
                "$and": [
                    {"team_id": {"$eq": team_id}},
                    {"channel_id": {"$eq": channel_id}},
                    {"is_active": {"$eq": True}},
                ]
            },
        )
        chunks: list[RetrievedChunk] = []
        if not results["documents"] or not results["documents"][0]:
            return chunks
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            score = 1.0 - float(dist)
            page = meta.get("page")
            chunks.append(
                RetrievedChunk(
                    text=doc,
                    score=score,
                    document_id=meta.get("document_id", ""),
                    title=meta.get("title", ""),
                    page=page if page and page >= 0 else None,
                    section=meta.get("section") or None,
                    source_url=meta.get("source_url") or None,
                    modified_at=meta.get("modified_at") or None,
                    language=meta.get("language") or None,
                    office=meta.get("office") or None,
                )
            )
        return chunks

    def count(self) -> int:
        return self._collection.count()


def get_vector_store() -> VectorStore:
    if settings.vector_db == "memory":
        from app.vectorstore.memory_store import MemoryVectorStore

        return MemoryVectorStore()
    if settings.vector_db == "qdrant":
        from app.vectorstore.qdrant_store import QdrantVectorStore

        return QdrantVectorStore()
    return ChromaVectorStore()
