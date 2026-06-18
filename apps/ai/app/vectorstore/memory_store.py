"""In-memory keyword retrieval for mock/dev — no local embedding models."""

import math
import re
from collections import Counter

from app.vectorstore.base import ChunkRecord, RetrievedChunk, VectorStore

_store: list[ChunkRecord] = []


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


class MemoryVectorStore:
    def upsert_chunks(self, chunks: list[ChunkRecord]) -> None:
        global _store
        ids = {c.chunk_id for c in chunks}
        _store = [c for c in _store if c.chunk_id not in ids]
        _store.extend(chunks)

    def search(self, query: str, team_id: str, channel_id: str, top_k: int) -> list[RetrievedChunk]:
        q_tokens = Counter(_tokenize(query))
        if not q_tokens:
            return []

        scored: list[tuple[float, ChunkRecord]] = []
        for chunk in _store:
            if chunk.team_id != team_id or chunk.channel_id != channel_id:
                continue
            doc_tokens = Counter(_tokenize(chunk.text))
            overlap = sum(q_tokens[t] * doc_tokens.get(t, 0) for t in q_tokens)
            if overlap == 0:
                continue
            norm = math.sqrt(sum(v * v for v in q_tokens.values())) * math.sqrt(
                sum(v * v for v in doc_tokens.values())
            )
            score = overlap / norm if norm else 0.0
            scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            RetrievedChunk(
                text=c.text,
                score=round(s, 4),
                document_id=c.document_id,
                title=c.title,
                page=c.page,
                section=c.section,
                source_url=c.source_url,
                modified_at=c.modified_at,
                language=c.language,
                office=c.office,
            )
            for s, c in scored[:top_k]
        ]

    def count(self) -> int:
        return len(_store)
