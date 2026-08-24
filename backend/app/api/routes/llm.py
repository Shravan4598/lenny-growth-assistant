from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.llm.factory import create_llm_provider


router = APIRouter(
    prefix="/llm",
    tags=["LLM"],
)


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