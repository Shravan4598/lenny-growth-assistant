from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, llm
from app.core.config import get_settings
from app.core.exceptions import (
    AppError,
    app_error_handler,
    unhandled_error_handler,
)
from app.core.logging import configure_logging, get_logger


settings = get_settings()

configure_logging(settings.log_level)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""

    logger.info(
        "application_starting",
        application=settings.app_name,
        environment=settings.environment,
        llm_provider=settings.llm_provider,
        model=(
            settings.ollama_model
            if settings.llm_provider == "ollama"
            else settings.cloud_model
        ),
    )

    yield

    logger.info(
        "application_stopping",
        application=settings.app_name,
    )


app = FastAPI(
    title=settings.app_name,
    description=(
        "A transcript-grounded product and growth assistant "
        "powered by Lenny's Podcast and Newsletter knowledge."
    ),
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Request-ID",
    ],
)


# Exception handlers
app.add_exception_handler(
    AppError,
    app_error_handler,
)

app.add_exception_handler(
    Exception,
    unhandled_error_handler,
)


# Root endpoint
@app.get(
    "/",
    tags=["root"],
)
def root() -> dict[str, str]:
    """Return basic application information."""

    return {
        "application": settings.app_name,
        "status": "running",
        "health": "/health",
        "api_docs": "/docs",
    }


# API routes
app.include_router(
    health.router,
)

app.include_router(
    llm.router,
    prefix=settings.api_prefix,
)