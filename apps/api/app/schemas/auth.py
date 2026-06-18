from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    entra_user_id: str
    email: str | None = None
    display_name: str | None = None
    tenant_id: str | None = None
    raw_token: str
