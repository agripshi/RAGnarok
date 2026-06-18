from dataclasses import dataclass


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
    location: str | None
