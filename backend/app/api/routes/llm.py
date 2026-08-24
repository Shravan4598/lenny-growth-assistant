from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings
from app.llm.factory import create_llm_provider


router = APIRouter(
    prefix="/llm",
    tags=["LLM"],
)


class GenerateRequest(BaseModel):
    """Request body for LLM generation."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=20_000,
    )

    temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
    )

    max_tokens: int | None = Field(
        default=None,
        ge=1,
    )


class GenerateResponse(BaseModel):
    """Normalized LLM generation response."""

    provider: str
    model: str
    response: str


@router.get("/status")
async def get_llm_status(
    settings: Settings = Depends(get_settings),
):
    """Return active LLM provider configuration and health."""

    provider = create_llm_provider(settings)

    health = await provider.health_check()

    return {
        "provider": health.provider,
        "model": health.model,
        "healthy": health.healthy,
        "detail": health.detail,
    }


@router.post(
    "/generate",
    response_model=GenerateResponse,
)
async def generate(
    request: GenerateRequest,
    settings: Settings = Depends(get_settings),
) -> GenerateResponse:
    """Generate a response using the configured LLM provider."""

    provider = create_llm_provider(settings)

    result = await provider.generate(
        request.prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )

    return GenerateResponse(
        provider=result.provider,
        model=result.model,
        response=result.content,
    )