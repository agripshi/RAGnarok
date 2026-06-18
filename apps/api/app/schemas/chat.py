from typing import Literal

from pydantic import BaseModel, Field

AnswerStatus = Literal["ANSWERED", "NEEDS_CLARIFICATION", "NOT_FOUND", "ACCESS_DENIED", "ERROR"]
SupportedLanguage = Literal["sq", "sr", "en", "unknown"]


class TeamsContextPayload(BaseModel):
    teamId: str | None = None
    channelId: str | None = None
    userId: str | None = None
    locale: str | None = None
    tenantId: str | None = None


class ChatRequest(BaseModel):
    conversationId: str | None = None
    message: str = Field(min_length=1, max_length=5000)
    teamsContext: TeamsContextPayload


class SourceCardDto(BaseModel):
    documentId: str | None = None
    title: str
    page: int | None = None
    section: str | None = None
    sourceUrl: str | None = None
    modifiedAt: str | None = None
    confidence: float | None = None


class ChatResponse(BaseModel):
    conversationId: str
    messageId: str
    status: AnswerStatus
    language: SupportedLanguage
    answer: str
    clarificationQuestion: str | None = None
    sources: list[SourceCardDto] = []


class MeResponse(BaseModel):
    userId: str
    email: str | None = None
    displayName: str | None = None
    hasHrAccess: bool
