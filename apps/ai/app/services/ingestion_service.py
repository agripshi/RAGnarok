import uuid
from pathlib import Path

from app.core.config import settings
from app.ingestion.pipeline import (
    SUPPORTED,
    detect_language_from_file,
    detect_office,
    extract_text,
    file_hash,
    load_sidecar_metadata,
    split_text,
)
from app.schemas.ingest import IngestRequest, IngestResponse
from app.vectorstore.base import ChunkRecord
from app.vectorstore.chroma_store import get_vector_store

_indexed_hashes: dict[str, str] = {}


class IngestionService:
    async def sync_documents(self, request: IngestRequest) -> IngestResponse:
        source = Path(request.source_path or settings.hr_docs_local_dir).resolve()
        if not source.exists():
            return IngestResponse(status="error", errors=[f"Source path not found: {source}"])

        store = get_vector_store()
        indexed_docs = 0
        indexed_chunks = 0
        skipped = 0
        errors: list[str] = []
        all_chunks: list[ChunkRecord] = []

        for path in sorted(source.iterdir()):
            if not path.is_file() or path.suffix.lower() not in SUPPORTED:
                continue
            try:
                content_hash = file_hash(path)
                key = str(path)
                if not request.force_reindex and _indexed_hashes.get(key) == content_hash:
                    skipped += 1
                    continue

                sidecar = load_sidecar_metadata(path)
                blocks = extract_text(path)
                if not blocks:
                    skipped += 1
                    continue

                full_text = "\n\n".join(b[0] for b in blocks)
                language = sidecar.get("language") or detect_language_from_file(path.name, full_text)
                office = sidecar.get("office") or detect_office(path.name)
                document_id = str(uuid.uuid5(uuid.NAMESPACE_URL, str(path)))
                modified_at = sidecar.get("modified_at") or datetime_iso(path)

                doc_chunks: list[ChunkRecord] = []
                for block_text, page, section in blocks:
                    for piece in split_text(block_text, settings.chunk_size, settings.chunk_overlap):
                        doc_chunks.append(
                            ChunkRecord(
                                chunk_id=str(uuid.uuid4()),
                                document_id=document_id,
                                text=piece,
                                title=path.name,
                                team_id=request.team_id,
                                channel_id=request.channel_id,
                                language=language,
                                office=office,
                                page=page,
                                section=section,
                                source_url=sidecar.get("source_url"),
                                modified_at=modified_at,
                                content_hash=content_hash,
                            )
                        )

                all_chunks.extend(doc_chunks)
                _indexed_hashes[key] = content_hash
                indexed_docs += 1
                indexed_chunks += len(doc_chunks)
            except Exception as e:
                errors.append(f"{path.name}: {e}")

        if all_chunks:
            store.upsert_chunks(all_chunks)

        return IngestResponse(
            status="ok" if not errors or indexed_docs > 0 else "error",
            indexed_documents=indexed_docs,
            indexed_chunks=indexed_chunks,
            skipped_documents=skipped,
            errors=errors,
        )


def datetime_iso(path: Path) -> str:
    from datetime import datetime, timezone

    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
