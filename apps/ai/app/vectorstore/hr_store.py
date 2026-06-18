from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore

from app.core.config import settings
from app.llm.embeddings import get_embeddings
from app.vectorstore.metadata import normalize_metadata

COLLECTION_NAME = "hr_documents"

_chroma_instance: Chroma | None = None
_memory_instance: InMemoryVectorStore | None = None


def scope_filter(team_id: str, channel_id: str, location: str) -> dict:
    return {
        "$and": [
            {"team_id": {"$eq": team_id}},
            {"channel_id": {"$eq": channel_id}},
            {"location": {"$eq": location}},
            {"is_active": {"$eq": True}},
        ]
    }


class HrVectorStore:
    def __init__(self, store: Chroma | InMemoryVectorStore) -> None:
        self._store = store

    def add_documents(self, documents: list[Document], ids: list[str] | None = None) -> None:
        if not documents:
            return
        prepared = [
            Document(page_content=doc.page_content, metadata=normalize_metadata(doc.metadata))
            for doc in documents
        ]
        self._store.add_documents(prepared, ids=ids)

    def similarity_search_with_relevance_scores(
        self,
        query: str,
        team_id: str,
        channel_id: str,
        location: str,
        top_k: int,
    ) -> list[tuple[Document, float]]:
        search_k = max(top_k * 3, top_k)
        if isinstance(self._store, InMemoryVectorStore):
            raw_results = self._store.similarity_search_with_score(query, k=search_k)
            results = [(doc, 1.0 / (1.0 + float(score))) for doc, score in raw_results]
        else:
            search_kwargs: dict = {
                "k": search_k,
                "filter": scope_filter(team_id, channel_id, location),
            }
            results = self._store.similarity_search_with_relevance_scores(
                query,
                **search_kwargs,
            )

        scoped = [
            (doc, score)
            for doc, score in results
            if doc.metadata.get("team_id") == team_id
            and doc.metadata.get("channel_id") == channel_id
            and doc.metadata.get("location") == location
            and doc.metadata.get("is_active") is True
        ]
        return scoped[:top_k]

    def count(self) -> int:
        if isinstance(self._store, Chroma):
            return self._store._collection.count()
        return len(self._store.store)


def _ensure_chroma_collection() -> None:
    persist = Path(settings.chroma_persist_dir)
    persist.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(persist))
    existing = {collection.name for collection in client.list_collections()}
    if COLLECTION_NAME not in existing:
        return

    collection = client.get_collection(COLLECTION_NAME)
    stored_model = (collection.metadata or {}).get("embedding_model")
    if stored_model and stored_model != settings.embedding_model:
        client.delete_collection(COLLECTION_NAME)


def _get_chroma_store() -> Chroma:
    global _chroma_instance
    if _chroma_instance is not None:
        return _chroma_instance

    _ensure_chroma_collection()
    persist = Path(settings.chroma_persist_dir)
    persist.mkdir(parents=True, exist_ok=True)
    _chroma_instance = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=str(persist),
        collection_metadata={
            "hnsw:space": "cosine",
            "embedding_model": settings.embedding_model,
            "embedding_provider": settings.embedding_provider,
        },
    )
    return _chroma_instance


def _get_memory_store() -> InMemoryVectorStore:
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = InMemoryVectorStore(get_embeddings())
    return _memory_instance


def get_vector_store() -> HrVectorStore:
    if settings.vector_db == "memory":
        return HrVectorStore(_get_memory_store())
    if settings.vector_db == "qdrant":
        from app.vectorstore.qdrant_store import get_qdrant_vector_store

        return get_qdrant_vector_store()
    return HrVectorStore(_get_chroma_store())
