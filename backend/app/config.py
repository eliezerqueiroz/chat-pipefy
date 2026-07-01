"""
Application configuration using Pydantic Settings.
All values are loaded from environment variables or the .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    # OpenAI (optional — only required when llm_provider="openai")
    openai_api_key: str = ""

    # LLM provider: "openai" | "ollama"
    # Default is "ollama" for 100% local, zero-cost operation.
    llm_provider: str = "ollama"

    # OpenAI models (used when llm_provider="openai")
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o"

    # Embedding dimension:
    # - text-embedding-3-small → 1536
    # - all-MiniLM-L6-v2 (ollama/local) → 384
    embedding_dim: int = 384

    # Ollama (used when llm_provider="ollama")
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "llama3"

    # Redis
    redis_url: str = "redis://redis:6379"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    allowed_origins: str = "http://localhost,http://localhost:3000,http://localhost:80"

    # RAG
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_results: int = 5
    max_history_messages: int = 10

    @model_validator(mode="after")
    def set_embedding_dim_for_provider(self) -> "Settings":
        """
        Auto-set embedding_dim based on the provider when not explicitly overridden:
        - openai  → 1536 (text-embedding-3-small)
        - ollama  → 384  (all-MiniLM-L6-v2)
        """
        if self.llm_provider == "openai" and self.embedding_dim == 384:
            object.__setattr__(self, "embedding_dim", 1536)
        return self

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse comma-separated ALLOWED_ORIGINS into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

