from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import AuthenticatedUser
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.auth_service import authenticate
from app.services.chat_service import handle_chat

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: AuthenticatedUser = Depends(authenticate),
    db: Session = Depends(get_db),
) -> ChatResponse:
    return await handle_chat(db, request, user)
