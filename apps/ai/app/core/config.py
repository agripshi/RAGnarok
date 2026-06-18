from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    ai_host: str = "0.0.0.0"
    ai_port: int = 8001
    ai_backend_internal_token: str = "dev-internal-token"
    test_mode: bool = False

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

    # Cloud embeddings — used when vector_db=chroma or qdrant
    embedding_provider: str = "openai"
    embedding_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    top_k: int = 6
    similarity_threshold: float = 0.15
    chunk_size: int = 900
    chunk_overlap: int = 120
    max_context_chunks: int = 6

    default_team_id: str = "1531e68a-4716-43aa-bc3b-41b11451cbbb"
    default_channel_id: str = "19:11b56c75623d48ac828e2797373cacae@thread.tacv2"
    hr_docs_local_dir: str = "../../data/hr-docs"


settings = Settings()
