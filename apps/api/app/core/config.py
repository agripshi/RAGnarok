from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "postgresql+psycopg://ragnarok:ragnarok@localhost:5432/ragnarok_hr"
    frontend_origins: str = "http://localhost:5173,https://localhost:53000"
    ai_backend_url: str = "http://localhost:8001"
    ai_backend_internal_token: str = "dev-internal-token"
    dev_auth_enabled: bool = True
    team_id: str = "demo-team-id"
    hr_private_channel_id: str = "demo-hr-channel-id"

    @property
    def frontend_origin_list(self) -> list[str]:
        return [o.strip() for o in self.frontend_origins.split(",") if o.strip()]


settings = Settings()
