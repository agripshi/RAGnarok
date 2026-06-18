from langchain_core.documents import Document

from app.vectorstore.base import RetrievedChunk


def normalize_metadata(metadata: dict) -> dict:
    normalized: dict = {}
    for key, value in metadata.items():
        if value is None:
            normalized[key] = ""
        elif isinstance(value, bool):
            normalized[key] = value
        elif isinstance(value, (int, float)):
            normalized[key] = value
        else:
            normalized[key] = str(value)
    return normalized


def document_to_retrieved_chunk(doc: Document, score: float) -> RetrievedChunk:
    meta = doc.metadata
    page = meta.get("page")
    if isinstance(page, str) and page.isdigit():
        page = int(page)
    if page is not None and page < 0:
        page = None

    def _optional_str(key: str) -> str | None:
        value = meta.get(key)
        if value is None or value == "":
            return None
        return str(value)

    return RetrievedChunk(
        text=doc.page_content,
        score=score,
        document_id=str(meta.get("document_id", "")),
        title=str(meta.get("title", "")),
        page=page if isinstance(page, int) else None,
        section=_optional_str("section"),
        source_url=_optional_str("source_url"),
        modified_at=_optional_str("modified_at"),
        language=_optional_str("language"),
        office=_optional_str("office"),
        location=_optional_str("location"),
    )
