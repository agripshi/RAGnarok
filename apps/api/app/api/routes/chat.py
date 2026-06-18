from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import AuthenticatedUser
from app.schemas.chat import ChatRequest, ChatResponse, MeResponse
from app.services.auth_service import authenticate
from app.services.access_guard import assert_user_can_access_hr_channel
from app.services.chat_service import handle_chat
from app.db.repositories import chat_repo

router = APIRouter()


@router.get("/me", response_model=MeResponse)
async def me(
    user: AuthenticatedUser = Depends(authenticate),
    db: Session = Depends(get_db),
) -> MeResponse:
    app_user = chat_repo.get_or_create_user(db, user.entra_user_id, user.email, user.display_name)
    has_access = True
    try:
        await assert_user_can_access_hr_channel(db, user)
    except Exception:
        has_access = False
    db.commit()
    return MeResponse(
        userId=str(app_user.id),
        email=user.email,
        displayName=user.display_name,
        hasHrAccess=has_access,
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: AuthenticatedUser = Depends(authenticate),
    db: Session = Depends(get_db),
) -> ChatResponse:
    return await handle_chat(db, request, user)
