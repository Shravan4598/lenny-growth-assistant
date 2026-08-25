from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.chat import ChatRequest, ChatResponse
from app.api.services.session_service import SessionService
from app.core.config import get_settings
from app.db.session import get_db
from app.llm.factory import create_llm_provider
from app.rag.service import RAGService
from app.retrieval.service import RetrievalService


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


def get_retrieval_service() -> RetrievalService:
    """
    Create and initialize the retrieval service.

    The FAISS index is loaded once when the dependency is created.
    """

    settings = get_settings()

    retrieval_service = RetrievalService(
        index_path=settings.retrieval_index_path,
        retrieval_embedding_model=settings.retrieval_embedding_model,
        min_score=settings.retrieval_min_score,
    )

    retrieval_service.load()

    return retrieval_service


def get_rag_service(
    retrieval_service: RetrievalService = Depends(
        get_retrieval_service
    ),
) -> RAGService:
    """Create the RAG service."""

    settings = get_settings()

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

    If session_id is provided, the conversation is persisted.
    """

    # ---------------------------------------------------------
    # 1. Validate session
    # ---------------------------------------------------------

    if request.session_id is not None:
        session_service.get_session(
            request.session_id,
        )

    # ---------------------------------------------------------
    # 2. Retrieve previous conversation BEFORE adding
    #    the current user message
    # ---------------------------------------------------------

    conversation_history = []

    if request.session_id is not None:
        messages = session_service.get_messages(
            request.session_id,
        )

        # Keep only the latest 10 messages.
        messages = messages[-10:]

        conversation_history = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]

    # ---------------------------------------------------------
    # 3. Save current user message
    # ---------------------------------------------------------

    if request.session_id is not None:
        session_service.add_message(
            session_id=request.session_id,
            role="user",
            content=request.prompt,
        )

    # ---------------------------------------------------------
    # 4. Run RAG
    # ---------------------------------------------------------

    result = await rag_service.answer(
        question=request.prompt,
        top_k=request.top_k,
        conversation_history=conversation_history,
    )

    # ---------------------------------------------------------
    # 5. Save assistant response
    # ---------------------------------------------------------

    if request.session_id is not None:
        session_service.add_message(
            session_id=request.session_id,
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
    # 6. Return response
    # ---------------------------------------------------------

    return ChatResponse(
        provider=result.provider,
        model=result.model,
        response=result.response,
        sources=result.sources,
    )