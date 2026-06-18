from typing import Literal

from pydantic import BaseModel

from app.core.locations import LocationCode


class IngestRequest(BaseModel):
    source_mode: Literal["local"] = "local"
    source_path: str | None = None
    team_id: str
    channel_id: str
    location: LocationCode | None = None
    force_reindex: bool = False


class IngestResponse(BaseModel):
    status: Literal["ok", "error"]
    indexed_documents: int = 0
    indexed_chunks: int = 0
    skipped_documents: int = 0
    errors: list[str] = []
