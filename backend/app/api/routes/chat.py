from functools import lru_cache
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.services.session_service import SessionService
from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.llm.factory import create_llm_provider
from app.rag.models import ChatRequest, ChatResponse
from app.rag.service import RAGService
from app.retrieval.service import RetrievalService


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@lru_cache(maxsize=1)
def get_retrieval_service(
    index_path: str,
) -> RetrievalService:
    """Create and cache the retrieval service."""

    service = RetrievalService(
        index_path=index_path,
    )

    service.load()

    return service


def get_rag_service(
    settings: Settings = Depends(get_settings),
) -> RAGService:
    """Create the RAG service."""

    index_path = Path(
        settings.retrieval_index_path,
    )

    retrieval_service = get_retrieval_service(
        str(index_path),
    )

    llm_provider = create_llm_provider(
        settings,
    )

    return RAGService(
        retrieval_service=retrieval_service,
        llm_provider=llm_provider,
    )


def get_session_service(
    db: Session = Depends(get_db),
) -> SessionService:
    """Create the session service."""

    return SessionService(db)


@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
    session_service: SessionService = Depends(get_session_service),
) -> ChatResponse:
    """
    Answer a question using retrieved Lenny knowledge.

    The conversation is persisted when a session_id is provided.
    """

    # ---------------------------------------------------------
    # 1. Validate session_id
    # ---------------------------------------------------------
    #
    # ChatRequest currently does not contain session_id.
    # Therefore this route temporarily supports session_id
    # through an optional request attribute.
    #
    # If session_id is added to ChatRequest later, this will
    # automatically use it.
    #
    session_id: UUID | None = getattr(
        request,
        "session_id",
        None,
    )

    # ---------------------------------------------------------
    # 2. Verify that the session exists
    # ---------------------------------------------------------
    if session_id is not None:
        session_service.get_session(
            session_id,
        )

    # ---------------------------------------------------------
    # 3. Save the user's message
    # ---------------------------------------------------------
    if session_id is not None:
        session_service.add_message(
            session_id=session_id,
            role="user",
            content=request.prompt,
        )

    # ---------------------------------------------------------
    # 4. Run RAG
    # ---------------------------------------------------------
    result = await rag_service.answer(
        question=request.prompt,
        top_k=request.top_k,
    )

    # ---------------------------------------------------------
    # 5. Save the assistant's response
    # ---------------------------------------------------------
    if session_id is not None:
        session_service.add_message(
            session_id=session_id,
            role="assistant",
            content=result.response,
            metadata={
                "provider": result.provider,
                "model": result.model,
                "sources": [
                    {
                        "chunk_id": source.chunk_id,
                        "title": source.title,
                        "guest": source.guest,
                        "date": source.date,
                        "source_url": source.source_url,
                        "score": source.score,
                    }
                    for source in result.sources
                ],
            },
        )

    # ---------------------------------------------------------
    # 6. Return the RAG response
    # ---------------------------------------------------------
    return result