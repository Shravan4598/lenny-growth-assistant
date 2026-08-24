from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

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

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/lenny_growth",
        alias="DATABASE_URL",
    )

    llm_provider: str = Field(
        default="ollama",
        alias="LLM_PROVIDER",
    )

    ollama_base_url: str = Field(
        default="http://localhost:11434",
        alias="OLLAMA_BASE_URL",
    )

    ollama_model: str = Field(
        default="qwen2.5:3b",
        alias="OLLAMA_MODEL",
    )

    cloud_provider: str | None = Field(
        default=None,
        alias="CLOUD_PROVIDER",
    )

    cloud_model: str | None = Field(
        default=None,
        alias="CLOUD_MODEL",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()