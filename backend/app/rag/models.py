from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request for a RAG-powered chat response."""

    prompt: str = Field(
        min_length=1,
        max_length=4000,
        description="User's question.",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of transcript chunks to retrieve.",
    )


class SourceResponse(BaseModel):
    """Source information returned with an answer."""

    chunk_id: str
    title: str
    guest: str | None = None
    date: str | None = None
    source_url: str | None = None
    score: float


class ChatResponse(BaseModel):
    """RAG response."""

    provider: str
    model: str
    response: str
    sources: list[SourceResponse]