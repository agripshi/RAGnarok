import uuid
from datetime import datetime, timezone
from pathlib import Path

from langchain_core.documents import Document

from app.core.config import settings
from app.core.locations import iter_location_files, location_to_language, location_to_office
from app.ingestion.loaders import get_document_loader
from app.ingestion.pipeline import (
    detect_language_from_file,
    detect_office,
    file_hash,
    load_sidecar_metadata,
)
from app.ingestion.splitter import get_text_splitter
from app.schemas.ingest import IngestRequest, IngestResponse
from app.vectorstore.hr_store import get_vector_store

_indexed_hashes: dict[str, str] = {}


class IngestionService:
    async def sync_documents(self, request: IngestRequest) -> IngestResponse:
        source = Path(request.source_path or settings.hr_docs_local_dir).resolve()
        if not source.exists():
            return IngestResponse(status="error", errors=[f"Source path not found: {source}"])

        store = get_vector_store()
        splitter = get_text_splitter()
        indexed_docs = 0
        indexed_chunks = 0
        skipped = 0
        errors: list[str] = []
        all_documents: list[Document] = []
        all_ids: list[str] = []

        for path, location in iter_location_files(source, request.location):
            try:
                content_hash = file_hash(path)
                key = str(path)
                if not request.force_reindex and _indexed_hashes.get(key) == content_hash:
                    skipped += 1
                    continue

                sidecar = load_sidecar_metadata(path)
                loader = get_document_loader(path)
                loaded_docs = loader.load()
                if not loaded_docs:
                    skipped += 1
                    continue

                full_text = "\n\n".join(doc.page_content for doc in loaded_docs)
                language = (
                    sidecar.get("language")
                    or detect_language_from_file(path.name, full_text)
                    or location_to_language(location)
                )
                office = (
                    sidecar.get("office")
                    or detect_office(path.name)
                    or location_to_office(location)
                )
                document_id = str(uuid.uuid5(uuid.NAMESPACE_URL, str(path)))
                modified_at = sidecar.get("modified_at") or _datetime_iso(path)

                enriched_docs: list[Document] = []
                for doc in loaded_docs:
                    page = doc.metadata.get("page")
                    if page is not None:
                        page = int(page) + 1

                    metadata = {
                        **doc.metadata,
                        "document_id": document_id,
                        "title": path.name,
                        "team_id": request.team_id,
                        "channel_id": request.channel_id,
                        "location": location,
                        "language": language or "",
                        "office": office or "",
                        "page": page if page is not None else -1,
                        "section": doc.metadata.get("section") or "",
                        "source_url": sidecar.get("source_url") or "",
                        "modified_at": modified_at or "",
                        "content_hash": content_hash,
                        "is_active": True,
                    }
                    enriched_docs.append(
                        Document(page_content=doc.page_content, metadata=metadata)
                    )

                split_docs = splitter.split_documents(enriched_docs)
                if not split_docs:
                    skipped += 1
                    continue

                for chunk in split_docs:
                    chunk_id = str(uuid.uuid4())
                    chunk.metadata["chunk_id"] = chunk_id
                    all_documents.append(chunk)
                    all_ids.append(chunk_id)

                _indexed_hashes[key] = content_hash
                indexed_docs += 1
                indexed_chunks += len(split_docs)
            except Exception as e:
                errors.append(f"{path.name}: {e}")

        if all_documents:
            store.add_documents(all_documents, ids=all_ids)

        return IngestResponse(
            status="ok" if not errors or indexed_docs > 0 else "error",
            indexed_documents=indexed_docs,
            indexed_chunks=indexed_chunks,
            skipped_documents=skipped,
            errors=errors,
        )


def _datetime_iso(path: Path) -> str:
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
