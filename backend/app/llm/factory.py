from app.core.config import Settings
from app.core.exceptions import AppError
from app.llm.base import LLMProvider
from app.llm.cloud import CloudProvider
from app.llm.ollama import OllamaProvider


def create_llm_provider(settings: Settings) -> LLMProvider:
    """Create the configured LLM provider."""

    if settings.llm_provider == "ollama":
        return OllamaProvider(settings)

    if settings.llm_provider == "cloud":
        return CloudProvider(settings)

    raise AppError(
        status_code=500,
        code="INVALID_LLM_PROVIDER",
        message=(
            f"Unsupported LLM provider: {settings.llm_provider}"
        ),
    )