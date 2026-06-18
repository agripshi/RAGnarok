from langchain_core.callbacks.manager import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from app.core.locations import LocationCode
from app.vectorstore.base import RetrievedChunk
from app.vectorstore.hr_store import HrVectorStore, get_vector_store
from app.vectorstore.metadata import document_to_retrieved_chunk


class ScopedHrRetriever(BaseRetriever):
    team_id: str
    channel_id: str
    location: LocationCode
    top_k: int = 6

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun | None = None,
    ) -> list[Document]:
        chunks = retrieve_chunks(
            query,
            self.team_id,
            self.channel_id,
            self.location,
            self.top_k,
        )
        return [
            Document(
                page_content=chunk.text,
                metadata={
                    "document_id": chunk.document_id,
                    "title": chunk.title,
                    "page": chunk.page if chunk.page is not None else -1,
                    "section": chunk.section or "",
                    "source_url": chunk.source_url or "",
                    "modified_at": chunk.modified_at or "",
                    "language": chunk.language or "",
                    "office": chunk.office or "",
                    "location": chunk.location or "",
                    "score": chunk.score,
                },
            )
            for chunk in chunks
        ]


def get_hr_retriever(
    team_id: str,
    channel_id: str,
    location: LocationCode,
    top_k: int,
    store: HrVectorStore | None = None,
) -> BaseRetriever:
    _ = store
    return ScopedHrRetriever(
        team_id=team_id,
        channel_id=channel_id,
        location=location,
        top_k=top_k,
    )


def retrieve_chunks(
    query: str,
    team_id: str,
    channel_id: str,
    location: LocationCode,
    top_k: int,
    store: HrVectorStore | None = None,
) -> list[RetrievedChunk]:
    vector_store = store or get_vector_store()
    results = vector_store.similarity_search_with_relevance_scores(
        query,
        team_id,
        channel_id,
        location,
        top_k,
    )
    return [document_to_retrieved_chunk(doc, score) for doc, score in results]
