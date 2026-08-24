import time

import httpx
import structlog

from app.core.config import Settings
from app.core.exceptions import AppException
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

    def __init__(self, settings: Settings):
        self._settings = settings

        if not settings.cloud_provider:
            raise AppException(
                status_code=500,
                code="CLOUD_PROVIDER_NOT_CONFIGURED",
                message="CLOUD_PROVIDER is required when LLM_PROVIDER=cloud.",
            )

        if not settings.cloud_base_url:
            raise AppException(
                status_code=500,
                code="CLOUD_BASE_URL_NOT_CONFIGURED",
                message="CLOUD_BASE_URL is required when LLM_PROVIDER=cloud.",
            )

        if not settings.cloud_api_key:
            raise AppException(
                status_code=500,
                code="CLOUD_API_KEY_MISSING",
                message=(
                    "Cloud LLM API key is missing. "
                    "Set CLOUD_API_KEY before using the cloud provider."
                ),
            )

        if not settings.cloud_model:
            raise AppException(
                status_code=500,
                code="CLOUD_MODEL_NOT_CONFIGURED",
                message="CLOUD_MODEL is required when LLM_PROVIDER=cloud.",
            )

        self._provider = settings.cloud_provider
        self._base_url = settings.cloud_base_url.rstrip("/")
        self._api_key = settings.cloud_api_key
        self._model = settings.cloud_model
        self._timeout = settings.llm_timeout_seconds

    @property
    def provider_name(self) -> str:
        return self._provider

    @property
    def model_name(self) -> str:
        return self._model

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    async def health_check(self) -> LLMHealthStatus:
        """
        Verify cloud endpoint reachability.

        We do not perform a billable generation request for a health check.
        """

        try:
            timeout = httpx.Timeout(self._timeout)

            async with httpx.AsyncClient(timeout=timeout) as client:
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

    async def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Generate text using an OpenAI-compatible chat endpoint."""

        started_at = time.perf_counter()

        payload = {
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

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers=self._headers(),
                    json=payload,
                )
                response.raise_for_status()

                response_payload = response.json()

        except httpx.TimeoutException as exc:
            raise AppException(
                status_code=504,
                code="LLM_TIMEOUT",
                message="Cloud model request timed out.",
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise AppException(
                status_code=503,
                code="CLOUD_LLM_REQUEST_FAILED",
                message=(
                    "Cloud LLM request failed. "
                    "Verify cloud provider configuration."
                ),
            ) from exc

        except httpx.HTTPError as exc:
            raise AppException(
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
            raise AppException(
                status_code=502,
                code="INVALID_LLM_RESPONSE",
                message="Cloud provider returned an unexpected response.",
            )

        content = choices[0].get("message", {}).get("content", "")

        return LLMResponse(
            content=content,
            model=response_payload.get("model", self._model),
            provider=self.provider_name,
            raw_response=response_payload,
        )