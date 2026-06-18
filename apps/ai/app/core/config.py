from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    ai_host: str = "0.0.0.0"
    ai_port: int = 8001
    ai_backend_internal_token: str = "dev-internal-token"

    vector_db: str = "memory"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "hr_documents"
    chroma_persist_dir: str = "./.chroma"

    # Cloud LLM — no local models (Ollama, etc.)
    llm_provider: str = "openai"
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.0
    llm_mock_enabled: bool = True

    # Cloud embeddings — used only when vector_db requires them
    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    top_k: int = 6
    similarity_threshold: float = 0.15
    chunk_size: int = 900
    chunk_overlap: int = 120
    max_context_chunks: int = 6

    default_team_id: str = "demo-team-id"
    default_channel_id: str = "demo-hr-channel-id"
    hr_docs_local_dir: str = "../../data/hr-docs"


settings = Settings()
