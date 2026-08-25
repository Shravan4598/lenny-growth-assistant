from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    """Request to create a new chat session."""

    title: str | None = Field(
        default=None,
        max_length=255,
    )


class SessionResponse(BaseModel):
    """Session information returned by the API."""

    id: UUID
    title: str | None
    created_at: datetime
    updated_at: datetime


class SessionMessageResponse(BaseModel):
    """Persisted conversation message."""

    id: UUID
    role: str
    content: str
    created_at: datetime


class SessionDetailResponse(BaseModel):
    """Session with its conversation history."""

    id: UUID
    title: str | None
    created_at: datetime
    updated_at: datetime
    messages: list[SessionMessageResponse]