import time

import httpx
import structlog

from app.core.config import Settings
from app.core.exceptions import AppError
from app.llm.base import LLMHealthStatus, LLMProvider, LLMResponse


logger = structlog.get_logger(__name__)


class CloudProvider(LLMProvider):
    """
    OpenAI-compatible cloud LLM provider.

    Required configuration:
    - CLOUD_PROVIDER
    - CLOUD_BASE_URL
    - CLOUD_API_KEY
    - CLOUD_MODEL
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

        if not settings.cloud_provider:
            raise AppError(
                status_code=500,
                code="CLOUD_PROVIDER_NOT_CONFIGURED",
                message=(
                    "CLOUD_PROVIDER is required when "
                    "LLM_PROVIDER=cloud."
                ),
            )

        if not settings.cloud_base_url:
            raise AppError(
                status_code=500,
                code="CLOUD_BASE_URL_NOT_CONFIGURED",
                message=(
                    "CLOUD_BASE_URL is required when "
                    "LLM_PROVIDER=cloud."
                ),
            )

        if not settings.cloud_api_key:
            raise AppError(
                status_code=500,
                code="CLOUD_API_KEY_MISSING",
                message=(
                    "Cloud LLM API key is missing. "
                    "Set CLOUD_API_KEY before using the cloud provider."
                ),
            )

        if not settings.cloud_model:
            raise AppError(
                status_code=500,
                code="CLOUD_MODEL_NOT_CONFIGURED",
                message=(
                    "CLOUD_MODEL is required when "
                    "LLM_PROVIDER=cloud."
                ),
            )

        self._provider = settings.cloud_provider
        self._base_url = settings.cloud_base_url.rstrip("/")
        self._api_key = settings.cloud_api_key
        self._model = settings.cloud_model
        self._timeout = settings.llm_timeout_seconds

    @property
    def provider_name(self) -> str:
        """Return the configured cloud provider name."""

        return self._provider

    @property
    def model_name(self) -> str:
        """Return the configured cloud model name."""

        return self._model

    def _headers(self) -> dict[str, str]:
        """Return authentication headers."""

        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    async def health_check(self) -> LLMHealthStatus:
        """
        Verify cloud endpoint reachability.

        No generation request is performed.
        """

        try:
            timeout = httpx.Timeout(self._timeout)

            async with httpx.AsyncClient(
                timeout=timeout
            ) as client:
                response = await client.get(
                    f"{self._base_url}/models",
                    headers=self._headers(),
                )

        except httpx.TimeoutException:
            return LLMHealthStatus(
                provider=self.provider_name,
                model=self.model_name,
                healthy=False,
                detail="Cloud provider health check timed out.",
            )

        except httpx.HTTPError:
            return LLMHealthStatus(
                provider=self.provider_name,
                model=self.model_name,
                healthy=False,
                detail="Cloud provider is unavailable.",
            )

        if response.status_code >= 400:
            return LLMHealthStatus(
                provider=self.provider_name,
                model=self.model_name,
                healthy=False,
                detail=(
                    f"Cloud provider returned HTTP "
                    f"{response.status_code}."
                ),
            )

        return LLMHealthStatus(
            provider=self.provider_name,
            model=self.model_name,
            healthy=True,
            detail="Cloud provider endpoint is reachable.",
        )

    async def model_available(self) -> tuple[bool, str]:
        """Check whether the configured cloud model is available."""

        try:
            timeout = httpx.Timeout(self._timeout)

            async with httpx.AsyncClient(
                timeout=timeout
            ) as client:
                response = await client.get(
                    f"{self._base_url}/models",
                    headers=self._headers(),
                )

                response.raise_for_status()

                payload = response.json()

        except httpx.TimeoutException:
            return False, "Cloud model check timed out."

        except httpx.HTTPError:
            return False, "Cloud provider is unavailable."

        models = payload.get("data", [])

        if not isinstance(models, list):
            return (
                False,
                "Cloud provider returned an invalid models response.",
            )

        model_names = {
            model.get("id")
            for model in models
            if isinstance(model, dict)
            and model.get("id")
        }

        if self._model in model_names:
            return (
                True,
                f"Configured model '{self._model}' is available.",
            )

        return (
            False,
            f"Configured model '{self._model}' is not available.",
        )

    async def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Generate text using an OpenAI-compatible chat endpoint."""

        if not prompt or not prompt.strip():
            raise AppError(
                status_code=400,
                code="INVALID_PROMPT",
                message="Prompt must not be empty.",
            )

        started_at = time.perf_counter()

        payload: dict = {
            "model": self._model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": temperature,
        }

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        try:
            timeout = httpx.Timeout(self._timeout)

            async with httpx.AsyncClient(
                timeout=timeout
            ) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers=self._headers(),
                    json=payload,
                )

                response.raise_for_status()

                response_payload = response.json()

        except httpx.TimeoutException as exc:
            raise AppError(
                status_code=504,
                code="LLM_TIMEOUT",
                message="Cloud model request timed out.",
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise AppError(
                status_code=503,
                code="CLOUD_LLM_REQUEST_FAILED",
                message=(
                    "Cloud LLM request failed. "
                    "Verify cloud provider configuration."
                ),
            ) from exc

        except httpx.HTTPError as exc:
            raise AppError(
                status_code=503,
                code="CLOUD_LLM_UNAVAILABLE",
                message="Cloud LLM service is unavailable.",
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

        choices = response_payload.get("choices", [])

        if not choices:
            raise AppError(
                status_code=502,
                code="INVALID_LLM_RESPONSE",
                message=(
                    "Cloud provider returned an unexpected response."
                ),
            )

        first_choice = choices[0]

        if not isinstance(first_choice, dict):
            raise AppError(
                status_code=502,
                code="INVALID_LLM_RESPONSE",
                message=(
                    "Cloud provider returned an invalid response."
                ),
            )

        message = first_choice.get("message", {})

        if not isinstance(message, dict):
            raise AppError(
                status_code=502,
                code="INVALID_LLM_RESPONSE",
                message=(
                    "Cloud provider returned an invalid message."
                ),
            )

        content = message.get("content", "")

        if not isinstance(content, str) or not content.strip():
            raise AppError(
                status_code=502,
                code="EMPTY_LLM_RESPONSE",
                message="Cloud provider returned an empty response.",
            )

        return LLMResponse(
            content=content.strip(),
            model=response_payload.get(
                "model",
                self._model,
            ),
            provider=self.provider_name,
            raw_response=response_payload,
        )