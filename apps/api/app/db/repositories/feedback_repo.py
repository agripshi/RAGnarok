import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AccessDeniedError, ConversationNotFoundError
from app.db.models import Feedback, Message, Conversation
from app.schemas.auth import AuthenticatedUser
from app.schemas.feedback import FeedbackRequest


def save_feedback(db: Session, user_id: uuid.UUID, request: FeedbackRequest) -> None:
    message = db.get(Message, uuid.UUID(request.messageId))
    if message is None:
        raise ConversationNotFoundError("Message not found.")
    conversation = db.get(Conversation, message.conversation_id)
    if conversation is None or conversation.user_id != user_id:
        raise ConversationNotFoundError("Message not found.")
    db.add(
        Feedback(
            message_id=message.id,
            user_id=user_id,
            rating=request.rating,
            comment=request.comment,
        )
    )


def is_admin(user: AuthenticatedUser) -> bool:
    emails = {e.strip().lower() for e in settings.admin_emails.split(",") if e.strip()}
    return bool(user.email and user.email.lower() in emails)
