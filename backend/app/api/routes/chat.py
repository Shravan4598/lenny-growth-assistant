from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
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


@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> ChatResponse:
    """Answer a question using retrieved Lenny knowledge."""

    return await rag_service.answer(
        question=request.prompt,
        top_k=request.top_k,
    )