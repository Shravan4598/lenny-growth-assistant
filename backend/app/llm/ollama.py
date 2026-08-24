import time

import httpx
import structlog

from app.core.config import Settings
from app.core.exceptions import AppError
from app.llm.base import LLMHealthStatus, LLMProvider, LLMResponse


logger = structlog.get_logger(__name__)


class OllamaProvider(LLMProvider):
    """LLM provider implementation for Ollama."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._base_url = settings.ollama_base_url.rstrip("/")
        self._model = settings.ollama_model
        self._timeout = settings.llm_timeout_seconds

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model

    async def health_check(self) -> LLMHealthStatus:
        """Verify that Ollama and the configured model are available."""

        try:
            timeout = httpx.Timeout(self._timeout)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(
                    f"{self._base_url}/api/tags"
                )
                response.raise_for_status()

                payload = response.json()

        except httpx.TimeoutException:
            logger.warning(
                "ollama_health_timeout",
                base_url=self._base_url,
            )

            return LLMHealthStatus(
                provider=self.provider_name,
                model=self.model_name,
                healthy=False,
                detail="Ollama health check timed out.",
            )

        except httpx.HTTPError as exc:
            logger.warning(
                "ollama_health_failed",
                base_url=self._base_url,
                error=str(exc),
            )

            return LLMHealthStatus(
                provider=self.provider_name,
                model=self.model_name,
                healthy=False,
                detail=(
                    "Local model service unavailable. "
                    "Start Ollama and verify it is running."
                ),
            )

        models = payload.get("models", [])

        model_names = {
            model.get("name")
            for model in models
            if model.get("name")
        }

        if self._model not in model_names:
            return LLMHealthStatus(
                provider=self.provider_name,
                model=self.model_name,
                healthy=False,
                detail=(
                    f"Configured Ollama model '{self._model}' "
                    "is not installed. Run the appropriate "
                    "ollama pull command."
                ),
            )

        return LLMHealthStatus(
            provider=self.provider_name,
            model=self.model_name,
            healthy=True,
            detail="Ollama service and configured model are available.",
        )

    async def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Generate text using Ollama."""

        started_at = time.perf_counter()

        options: dict[str, float | int] = {
            "temperature": temperature,
        }

        if max_tokens is not None:
            options["num_predict"] = max_tokens

        request_payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "options": options,
        }

        try:
            timeout = httpx.Timeout(self._timeout)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self._base_url}/api/generate",
                    json=request_payload,
                )
                response.raise_for_status()

                payload = response.json()

        except httpx.TimeoutException as exc:
            logger.warning(
                "ollama_generation_timeout",
                model=self._model,
                timeout_seconds=self._timeout,
            )

            raise AppError(
                status_code=504,
                code="LLM_TIMEOUT",
                message=(
                    "The local model took too long to respond. "
                    "Try again or increase LLM_TIMEOUT_SECONDS."
                ),
            ) from exc

        except httpx.HTTPError as exc:
            logger.error(
                "ollama_generation_failed",
                model=self._model,
                error=str(exc),
            )

            raise AppError(
                status_code=503,
                code="OLLAMA_UNAVAILABLE",
                message=(
                    "Local model service unavailable. "
                    "Start Ollama and verify the configured model "
                    "is installed."
                ),
            ) from exc

        duration_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        logger.info(
            "llm_request_completed",
            provider=self.provider_name,
            model=self.model_name,
            duration_ms=duration_ms,
        )

        return LLMResponse(
            content=payload.get("response", ""),
            model=payload.get("model", self._model),
            provider=self.provider_name,
            raw_response=payload,
        )