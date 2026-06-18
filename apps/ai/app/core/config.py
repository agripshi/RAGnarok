from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    ai_host: str = "0.0.0.0"
    ai_port: int = 8001
    ai_backend_internal_token: str = "dev-internal-token"
    vector_db: str = "qdrant"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "hr_documents"
    default_team_id: str = "demo-team-id"
    default_channel_id: str = "demo-hr-channel-id"
    hr_docs_local_dir: str = "../../data/hr-docs"
    top_k: int = 6
    similarity_threshold: float = 0.72
    chunk_size: int = 900
    chunk_overlap: int = 120
    llm_temperature: float = 0.0


settings = Settings()
