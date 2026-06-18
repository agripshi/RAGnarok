import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AppUser, Conversation, Message, AnswerSource, AccessCheckCache


def get_or_create_user(db: Session, entra_user_id: str, email: str | None, display_name: str | None) -> AppUser:
    user = db.scalar(select(AppUser).where(AppUser.entra_user_id == entra_user_id))
    if user:
        if email and user.email != email:
            user.email = email
        if display_name and user.display_name != display_name:
            user.display_name = display_name
        return user
    user = AppUser(entra_user_id=entra_user_id, email=email, display_name=display_name)
    db.add(user)
    db.flush()
    return user


def create_conversation(db: Session, user_id: uuid.UUID, title: str) -> Conversation:
    conv = Conversation(user_id=user_id, title=title[:200])
    db.add(conv)
    db.flush()
    return conv


def get_conversation_for_user(db: Session, conversation_id: uuid.UUID, user_id: uuid.UUID) -> Conversation | None:
    return db.scalar(
        select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id)
    )


def add_message(
    db: Session,
    conversation_id: uuid.UUID,
    role: str,
    content: str,
    language: str | None = None,
    status: str | None = None,
) -> Message:
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        language=language,
        status=status,
    )
    db.add(msg)
    db.flush()
    return msg


def _safe_uuid(value: str | None) -> uuid.UUID | None:
    if not value:
        return None
    try:
        return uuid.UUID(str(value))
    except ValueError:
        return None


def add_answer_sources(db: Session, message_id: uuid.UUID, sources: list[dict]) -> None:
    for src in sources:
        db.add(
            AnswerSource(
                message_id=message_id,
                document_id=_safe_uuid(src.get("documentId")),
                title=src["title"],
                page=src.get("page"),
                section=src.get("section"),
                source_url=src.get("sourceUrl"),
                score=src.get("confidence"),
            )
        )


def get_cached_access(
    db: Session, entra_user_id: str, team_id: str, channel_id: str
) -> AccessCheckCache | None:
    from datetime import datetime, timezone

    return db.scalar(
        select(AccessCheckCache).where(
            AccessCheckCache.entra_user_id == entra_user_id,
            AccessCheckCache.team_id == team_id,
            AccessCheckCache.channel_id == channel_id,
            AccessCheckCache.expires_at > datetime.now(timezone.utc),
        )
    )


def set_cached_access(
    db: Session, entra_user_id: str, team_id: str, channel_id: str, allowed: bool, expires_at
) -> None:
    existing = db.scalar(
        select(AccessCheckCache).where(
            AccessCheckCache.entra_user_id == entra_user_id,
            AccessCheckCache.team_id == team_id,
            AccessCheckCache.channel_id == channel_id,
        )
    )
    if existing:
        existing.allowed = allowed
        existing.expires_at = expires_at
    else:
        db.add(
            AccessCheckCache(
                entra_user_id=entra_user_id,
                team_id=team_id,
                channel_id=channel_id,
                allowed=allowed,
                expires_at=expires_at,
            )
        )
