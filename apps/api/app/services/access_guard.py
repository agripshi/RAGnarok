from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AccessDeniedError
from app.db.repositories import chat_repo
from app.schemas.auth import AuthenticatedUser


def _is_allowlisted(user: AuthenticatedUser) -> bool:
    emails = {e.strip().lower() for e in settings.authorized_emails.split(",") if e.strip()}
    user_ids = {u.strip() for u in settings.authorized_user_ids.split(",") if u.strip()}
    if user.email and user.email.lower() in emails:
        return True
    return user.entra_user_id in user_ids


async def assert_user_can_access_hr_channel(db: Session, user: AuthenticatedUser) -> None:
    team_id = settings.team_id
    channel_id = settings.hr_private_channel_id

    cached = chat_repo.get_cached_access(db, user.entra_user_id, team_id, channel_id)
    if cached is not None:
        if cached.allowed:
            return
        raise AccessDeniedError()

    allowed = _is_allowlisted(user)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.access_cache_ttl_seconds)
    chat_repo.set_cached_access(db, user.entra_user_id, team_id, channel_id, allowed, expires_at)
    db.commit()

    if not allowed:
        raise AccessDeniedError()
