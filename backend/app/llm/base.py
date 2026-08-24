from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class LLMHealthStatus:
    """Health information returned by an LLM provider."""

    provider: str
    model: str
    healthy: bool
    detail: str


@dataclass
class LLMResponse:
    """Normalized response returned by all LLM providers."""

    content: str
    model: str
    provider: str
    raw_response: dict[str, Any] | None = None


class LLMProvider(ABC):
    """Abstract interface implemented by all LLM providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the configured model name."""

    @abstractmethod
    async def health_check(self) -> LLMHealthStatus:
        """Check provider and configured model availability."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Generate a response from the configured model."""