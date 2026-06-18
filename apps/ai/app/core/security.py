from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

_bearer = HTTPBearer(auto_error=False)


def require_internal_token(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> None:
    if credentials is None or credentials.credentials != settings.ai_backend_internal_token:
        raise HTTPException(status_code=401, detail="Invalid or missing internal token")
