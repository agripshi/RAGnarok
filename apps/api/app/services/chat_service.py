from sqlalchemy.orm import Session

from app.core.errors import ConversationNotFoundError
from app.db.repositories import chat_repo
from app.schemas.auth import AuthenticatedUser
from app.schemas.chat import ChatRequest, ChatResponse, SourceCardDto
from app.services.access_guard import assert_user_can_access_hr_channel


async def handle_chat(db: Session, request: ChatRequest, user: AuthenticatedUser) -> ChatResponse:
    await assert_user_can_access_hr_channel(db, user)

    app_user = chat_repo.get_or_create_user(
        db, user.entra_user_id, user.email, user.display_name
    )

    if request.conversationId:
        import uuid

        conversation = chat_repo.get_conversation_for_user(
            db, uuid.UUID(request.conversationId), app_user.id
        )
        if conversation is None:
            raise ConversationNotFoundError()
    else:
        title = request.message.strip()[:80] or "New conversation"
        conversation = chat_repo.create_conversation(db, app_user.id, title)

    chat_repo.add_message(db, conversation.id, "user", request.message)

    # Sprint 1 stub — real AI integration in Sprint 3
    stub_sources = [
        SourceCardDto(
            title="HR Policy Demo",
            page=1,
            section="Leave Policy",
            confidence=0.9,
        )
    ]
    assistant = chat_repo.add_message(
        db,
        conversation.id,
        "assistant",
        "This is a Sprint 1 stub response. AI RAG integration arrives in Sprint 3.",
        language="en",
        status="ANSWERED",
    )
    chat_repo.add_answer_sources(
        db,
        assistant.id,
        [s.model_dump() for s in stub_sources],
    )
    db.commit()

    return ChatResponse(
        conversationId=str(conversation.id),
        messageId=str(assistant.id),
        status="ANSWERED",
        language="en",
        answer=assistant.content,
        sources=stub_sources,
    )
