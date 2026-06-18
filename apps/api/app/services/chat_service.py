from datetime import datetime, timezone

import uuid

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AiBackendError, ConversationNotFoundError
from app.db.repositories import chat_repo
from app.schemas.auth import AuthenticatedUser
from app.schemas.chat import ChatRequest, ChatResponse, SourceCardDto
from app.services.access_guard import assert_user_can_access_hr_channel
from app.services.ai_client import AiAnswerRequest, AiAnswerResponse


async def call_ai_backend(payload: AiAnswerRequest) -> AiAnswerResponse:
    url = f"{settings.ai_backend_url.rstrip('/')}/ai/rag/answer"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                json=payload.model_dump(),
                headers={"Authorization": f"Bearer {settings.ai_backend_internal_token}"},
            )
            response.raise_for_status()
            return AiAnswerResponse.model_validate(response.json())
    except httpx.HTTPError as e:
        raise AiBackendError(str(e)) from e


async def handle_chat(db: Session, request: ChatRequest, user: AuthenticatedUser) -> ChatResponse:
    await assert_user_can_access_hr_channel(db, user)

    app_user = chat_repo.get_or_create_user(
        db, user.entra_user_id, user.email, user.display_name
    )

    if request.conversationId:
        conversation = chat_repo.get_conversation_for_user(
            db, uuid.UUID(request.conversationId), app_user.id
        )
        if conversation is None:
            raise ConversationNotFoundError()
    else:
        title = request.message.strip()[:80] or "New conversation"
        conversation = chat_repo.create_conversation(db, app_user.id, title)

    chat_repo.add_message(db, conversation.id, "user", request.message)

    recent = _load_recent_messages(db, conversation.id)
    ai_request = AiAnswerRequest(
        request_id=str(uuid.uuid4()),
        user_id=str(app_user.id),
        conversation_id=str(conversation.id),
        question=request.message,
        recent_messages=recent,
        authorization_scope={
            "team_id": settings.team_id,
            "channel_id": settings.hr_private_channel_id,
            "allowed": True,
        },
        response_language_hint=request.teamsContext.locale,
    )
    ai_response = await call_ai_backend(ai_request)

    answer_text = ai_response.answer
    if ai_response.clarification_question and ai_response.status == "NEEDS_CLARIFICATION":
        answer_text = ai_response.clarification_question

    assistant = chat_repo.add_message(
        db,
        conversation.id,
        "assistant",
        answer_text,
        language=ai_response.language,
        status=ai_response.status,
    )
    if ai_response.sources:
        chat_repo.add_answer_sources(
            db,
            assistant.id,
            [s.model_dump() for s in ai_response.sources],
        )
    conversation.updated_at = datetime.now(timezone.utc)
    db.commit()

    return ChatResponse(
        conversationId=str(conversation.id),
        messageId=str(assistant.id),
        status=ai_response.status,
        language=ai_response.language if ai_response.language in ("sq", "sr", "en") else "unknown",
        answer=answer_text,
        clarificationQuestion=ai_response.clarification_question,
        sources=ai_response.sources,
    )


def _load_recent_messages(db: Session, conversation_id: uuid.UUID, limit: int = 6) -> list[dict]:
    from sqlalchemy import select
    from app.db.models import Message

    rows = db.scalars(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    ).all()
    return [{"role": m.role, "content": m.content} for m in reversed(rows)]
