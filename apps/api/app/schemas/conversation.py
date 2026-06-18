from typing import Literal

from pydantic import BaseModel

from app.schemas.chat import AnswerStatus, SourceCardDto, SupportedLanguage


class ConversationSummaryDto(BaseModel):
    id: str
    title: str
    createdAt: str
    updatedAt: str


class MessageDto(BaseModel):
    id: str
    conversationId: str
    role: Literal["user", "assistant", "system"]
    content: str
    status: AnswerStatus | None = None
    language: SupportedLanguage | None = None
    sources: list[SourceCardDto] = []
    createdAt: str


class ConversationDetailDto(BaseModel):
    id: str
    title: str
    createdAt: str
    updatedAt: str
    messages: list[MessageDto]
