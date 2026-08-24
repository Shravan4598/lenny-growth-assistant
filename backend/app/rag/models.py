from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for RAG chat."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=20_000,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
    )


class SourceResponse(BaseModel):
    """Metadata for a retrieved source."""

    chunk_id: str
    title: str
    guest: str | None = None
    date: str | None = None
    source_url: str | None = None
    score: float


class ChatResponse(BaseModel):
    """Response from the RAG pipeline."""

    provider: str
    model: str
    response: str
    sources: list[SourceResponse]