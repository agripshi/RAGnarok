from dataclasses import dataclass
from typing import Protocol


@dataclass
class ChunkRecord:
    chunk_id: str
    document_id: str
    text: str
    title: str
    team_id: str
    channel_id: str
    language: str | None
    office: str | None
    page: int | None
    section: str | None
    source_url: str | None
    modified_at: str | None
    content_hash: str


@dataclass
class RetrievedChunk:
    text: str
    score: float
    document_id: str
    title: str
    page: int | None
    section: str | None
    source_url: str | None
    modified_at: str | None
    language: str | None
    office: str | None


class VectorStore(Protocol):
    def upsert_chunks(self, chunks: list[ChunkRecord]) -> None: ...
    def search(
        self, query: str, team_id: str, channel_id: str, top_k: int
    ) -> list[RetrievedChunk]: ...
    def count(self) -> int: ...
