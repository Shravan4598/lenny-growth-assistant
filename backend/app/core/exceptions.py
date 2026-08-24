from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.logging import get_logger


logger = get_logger(__name__)


class AppError(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        code: str = "internal_error",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}
        super().__init__(message)


class DatabaseUnavailableError(AppError):
    """Raised when the database is unavailable."""

    def __init__(self) -> None:
        super().__init__(
            message="The conversation database is temporarily unavailable.",
            status_code=503,
            code="database_unavailable",
        )


class ConfigurationError(AppError):
    """Raised when required configuration is invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            status_code=500,
            code="configuration_error",
        )


async def app_error_handler(
    request: Request,
    exc: AppError,
) -> JSONResponse:
    """Return structured responses for expected application errors."""

    logger.error(
        "application_error",
        path=request.url.path,
        method=request.method,
        error_code=exc.code,
        status_code=exc.status_code,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


async def unhandled_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle unexpected exceptions without exposing internals."""

    logger.exception(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "An unexpected server error occurred.",
                "details": {},
            }
        },
    )