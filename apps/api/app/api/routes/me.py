import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.repositories import chat_repo
from app.db.repositories.feedback_repo import is_admin, save_feedback
from app.db.session import get_db
from app.schemas.auth import AuthenticatedUser
from app.schemas.chat import MeResponse
from app.schemas.feedback import FeedbackRequest
from app.services.auth_service import authenticate
from app.services.access_guard import assert_user_can_access_hr_channel
from app.services.ingestion_orchestrator import trigger_ai_ingest
from app.core.errors import AccessDeniedError

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


@router.post("/feedback")
async def feedback(
    request: FeedbackRequest,
    user: AuthenticatedUser = Depends(authenticate),
    db: Session = Depends(get_db),
) -> dict:
    app_user = chat_repo.get_or_create_user(db, user.entra_user_id, user.email, user.display_name)
    save_feedback(db, app_user.id, request)
    db.commit()
    return {"ok": True}


@router.post("/admin/ingest/sync")
async def admin_ingest_sync(
    user: AuthenticatedUser = Depends(authenticate),
) -> dict:
    if not is_admin(user):
        raise AccessDeniedError("Admin access required.")
    return await trigger_ai_ingest()
