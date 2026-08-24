from datetime import datetime, timezone

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.db.session import check_database_connection


router = APIRouter(
    prefix="/health",
    tags=["health"],
)


settings = get_settings()


class HealthResponse(BaseModel):
    status: str
    application: str
    environment: str
    timestamp: datetime


class ReadinessResponse(HealthResponse):
    database: str
    llm_provider: str
    model: str


@router.get(
    "",
    response_model=HealthResponse,
)
def health_check() -> HealthResponse:
    """Check whether the FastAPI application is running."""

    return HealthResponse(
        status="ok",
        application=settings.app_name,
        environment=settings.environment,
        timestamp=datetime.now(timezone.utc),
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
)
def readiness_check() -> ReadinessResponse:
    """Check whether critical dependencies are available."""

    database_available = check_database_connection()

    if not database_available:
        database_status = "unavailable"
        application_status = "degraded"
        response_status = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        database_status = "available"
        application_status = "ok"
        response_status = status.HTTP_200_OK

    response = ReadinessResponse(
        status=application_status,
        application=settings.app_name,
        environment=settings.environment,
        timestamp=datetime.now(timezone.utc),
        database=database_status,
        llm_provider=settings.llm_provider,
        model=(
            settings.ollama_model
            if settings.llm_provider == "ollama"
            else settings.cloud_model or "not_configured"
        ),
    )

    # FastAPI does not infer the status code from a Pydantic response model,
    # so this will be handled through the route decorator in the next revision
    # if degraded responses need explicit HTTP status handling.
    return response



'''
from datetime import datetime, timezone

from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.db.session import check_database_connection


router = APIRouter(
    prefix="/health",
    tags=["health"],
)

settings = get_settings()


class HealthResponse(BaseModel):
    status: str
    application: str
    environment: str
    timestamp: datetime


class ReadinessResponse(HealthResponse):
    database: str
    llm_provider: str
    model: str


@router.get(
    "",
    response_model=HealthResponse,
)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        application=settings.app_name,
        environment=settings.environment,
        timestamp=datetime.now(timezone.utc),
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
)
def readiness_check(response: Response) -> ReadinessResponse:
    database_available = check_database_connection()

    if database_available:
        application_status = "ok"
        database_status = "available"
    else:
        application_status = "degraded"
        database_status = "unavailable"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(
        status=application_status,
        application=settings.app_name,
        environment=settings.environment,
        timestamp=datetime.now(timezone.utc),
        database=database_status,
        llm_provider=settings.llm_provider,
        model=(
            settings.ollama_model
            if settings.llm_provider == "ollama"
            else settings.cloud_model or "not_configured"
        ),
    )
'''