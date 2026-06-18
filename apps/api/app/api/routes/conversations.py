from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import AuthenticatedUser
from app.schemas.conversation import ConversationDetailDto, ConversationSummaryDto
from app.services.auth_service import authenticate
from app.services.conversation_service import get_conversation, list_conversations

router = APIRouter()


@router.get("/conversations", response_model=list[ConversationSummaryDto])
async def conversations(
    user: AuthenticatedUser = Depends(authenticate),
    db: Session = Depends(get_db),
) -> list[ConversationSummaryDto]:
    return list_conversations(db, user)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailDto)
async def conversation_detail(
    conversation_id: str,
    user: AuthenticatedUser = Depends(authenticate),
    db: Session = Depends(get_db),
) -> ConversationDetailDto:
    return get_conversation(db, user, conversation_id)
