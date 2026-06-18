import uuid

from sqlalchemy.orm import Session

from app.core.errors import ConversationNotFoundError
from app.db.repositories import chat_repo
from app.schemas.auth import AuthenticatedUser
from app.schemas.chat import SourceCardDto
from app.schemas.conversation import ConversationDetailDto, ConversationSummaryDto, MessageDto


def _iso(dt) -> str:
    return dt.isoformat()


def _source_dto(src) -> SourceCardDto:
    return SourceCardDto(
        documentId=str(src.document_id) if src.document_id else None,
        title=src.title,
        page=src.page,
        section=src.section,
        sourceUrl=src.source_url,
        confidence=src.score,
    )


def list_conversations(db: Session, user: AuthenticatedUser) -> list[ConversationSummaryDto]:
    app_user = chat_repo.get_or_create_user(db, user.entra_user_id, user.email, user.display_name)
    rows = chat_repo.list_conversations_for_user(db, app_user.id)
    db.commit()
    return [
        ConversationSummaryDto(
            id=str(c.id),
            title=c.title,
            createdAt=_iso(c.created_at),
            updatedAt=_iso(c.updated_at),
        )
        for c in rows
    ]


def get_conversation(db: Session, user: AuthenticatedUser, conversation_id: str) -> ConversationDetailDto:
    app_user = chat_repo.get_or_create_user(db, user.entra_user_id, user.email, user.display_name)
    conv = chat_repo.get_conversation_for_user(db, uuid.UUID(conversation_id), app_user.id)
    if conv is None:
        raise ConversationNotFoundError()

    messages = chat_repo.get_messages_for_conversation(db, conv.id)
    db.commit()

    return ConversationDetailDto(
        id=str(conv.id),
        title=conv.title,
        createdAt=_iso(conv.created_at),
        updatedAt=_iso(conv.updated_at),
        messages=[
            MessageDto(
                id=str(m.id),
                conversationId=str(conv.id),
                role=m.role,  # type: ignore[arg-type]
                content=m.content,
                status=m.status,  # type: ignore[arg-type]
                language=m.language if m.language in ("sq", "sr", "en") else None,
                sources=[_source_dto(s) for s in m.answer_sources] if m.role == "assistant" else [],
                createdAt=_iso(m.created_at),
            )
            for m in messages
            if m.role in ("user", "assistant")
        ],
    )
