from pydantic import BaseModel

from app.schemas.chat import SourceCardDto


class AiAnswerRequest(BaseModel):
    request_id: str
    user_id: str
    conversation_id: str
    question: str
    location: str = "al"  # branch filter: "al" = Albania, "sr" = Serbia
    recent_messages: list[dict]
    authorization_scope: dict
    response_language_hint: str | None = None


class AiAnswerResponse(BaseModel):
    status: str
    language: str
    answer: str
    clarification_question: str | None = None
    sources: list[SourceCardDto] = []
