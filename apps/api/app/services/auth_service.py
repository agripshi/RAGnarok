from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.errors import AuthenticationError
from app.schemas.auth import AuthenticatedUser

_bearer = HTTPBearer(auto_error=False)


def authenticate(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> AuthenticatedUser:
    if credentials is None:
        raise AuthenticationError()

    token = credentials.credentials

    if settings.dev_auth_enabled and token == "dev-token":
        return AuthenticatedUser(
            entra_user_id=settings.dev_auth_user_id,
            email=settings.dev_auth_email,
            display_name="Demo User",
            tenant_id="local",
            raw_token=token,
        )

    raise AuthenticationError("Teams SSO validation not configured for MVP. Use dev-token locally.")
