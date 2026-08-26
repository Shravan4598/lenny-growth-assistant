from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    app_name: str = Field(
        default="The Lenny Growth Assistant",
        alias="APP_NAME",
    )

    environment: str = Field(
        default="development",
        alias="ENVIRONMENT",
    )

    debug: bool = Field(
        default=False,
        alias="DEBUG",
    )

    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
    )

    api_prefix: str = Field(
        default="/api/v1",
        alias="API_PREFIX",
    )

    cors_origins: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8501",
        ],
        alias="CORS_ORIGINS",
    )

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    database_url: str = Field(
        default=(
            "postgresql+psycopg://postgres:"
            "postgres@localhost:5432/lenny_growth"
        ),
        alias="DATABASE_URL",
    )

    # ------------------------------------------------------------------
    # LLM provider selection
    # ------------------------------------------------------------------

    llm_provider: str = Field(
        default="ollama",
        alias="LLM_PROVIDER",
    )

    llm_timeout_seconds: float = Field(
        default=60.0,
        alias="LLM_TIMEOUT_SECONDS",
    )

    # ------------------------------------------------------------------
    # Ollama
    # ------------------------------------------------------------------

    ollama_base_url: str = Field(
        default="http://localhost:11434",
        alias="OLLAMA_BASE_URL",
    )

    ollama_model: str = Field(
        default="qwen2.5:3b",
        alias="OLLAMA_MODEL",
    )

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    retrieval_index_path: str = Field(
        default="data/index/lenny.faiss",
        alias="RETRIEVAL_INDEX_PATH",
    )

    retrieval_top_k: int = Field(
        default=5,
        alias="RETRIEVAL_TOP_K",
    )

    retrieval_min_score: float = Field(
        default=0.40,
        alias="RETRIEVAL_MIN_SCORE",
    )

    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        alias="EMBEDDING_MODEL",
    )

    # ------------------------------------------------------------------
    # Lenny Knowledge Base
    # ------------------------------------------------------------------

    lenny_repository_path: str = Field(
        default="data/external/lennys-newsletterpodcastdata",
        alias="LENNY_REPOSITORY_PATH",
    )

    lenny_content_types: list[str] = Field(
        default=["podcasts", "newsletters"],
        alias="LENNY_CONTENT_TYPES",
    )

    # ------------------------------------------------------------------
    # Cloud provider
    # ------------------------------------------------------------------

    cloud_provider: str | None = Field(
        default=None,
        alias="CLOUD_PROVIDER",
    )

    cloud_base_url: str | None = Field(
        default=None,
        alias="CLOUD_BASE_URL",
    )

    cloud_api_key: str | None = Field(
        default=None,
        alias="CLOUD_API_KEY",
    )

    cloud_model: str | None = Field(
        default=None,
        alias="CLOUD_MODEL",
    )

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        """Parse JSON lists or comma-separated frontend origins."""

        if isinstance(value, list):
            return value

        if isinstance(value, str):
            value = value.strip()

            if value.startswith("["):
                import json

                return json.loads(value)

            return [
                origin.strip()
                for origin in value.split(",")
                if origin.strip()
            ]

        return value

    @field_validator("llm_provider")
    @classmethod
    def validate_llm_provider(cls, value: str) -> str:
        """Validate configured LLM provider."""

        normalized = value.strip().lower()

        allowed_providers = {"ollama", "cloud"}

        if normalized not in allowed_providers:
            raise ValueError(
                "LLM_PROVIDER must be either 'ollama' or 'cloud'."
            )

        return normalized


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()