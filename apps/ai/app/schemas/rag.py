from typing import Literal

from pydantic import BaseModel, Field

from app.core.locations import LocationCode

AnswerStatus = Literal["ANSWERED", "NEEDS_CLARIFICATION", "NOT_FOUND", "ACCESS_DENIED", "ERROR"]


class RecentMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class AuthorizationScope(BaseModel):
    team_id: str
    channel_id: str
    allowed: bool


class RagAnswerRequest(BaseModel):
    request_id: str
    user_id: str
    conversation_id: str
    question: str = Field(min_length=1, max_length=5000)
    location: LocationCode
    recent_messages: list[RecentMessage] = []
    authorization_scope: AuthorizationScope
    response_language_hint: str | None = None


class SourceDto(BaseModel):
    documentId: str | None = None
    title: str
    page: int | None = None
    section: str | None = None
    sourceUrl: str | None = None
    modifiedAt: str | None = None
    confidence: float | None = None
    location: str | None = None


class RagAnswerResponse(BaseModel):
    status: AnswerStatus
    language: str
    answer: str
    clarification_question: str | None = None
    sources: list[SourceDto] = []
