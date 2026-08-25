"""Tools available to the agent during skill execution."""

from dataclasses import dataclass
from app.retrieval.service import RetrievalService
from app.retrieval.models import RetrievedChunk


@dataclass
class ToolContext:
    """Context provided to tools during execution."""

    retrieval_service: RetrievalService
    conversation_history: list[dict[str, str]]


class RetrievalTool:
    """Tool for retrieving transcript knowledge."""

    def __init__(self, retrieval_service: RetrievalService) -> None:
        self.retrieval_service = retrieval_service

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Retrieve relevant transcript chunks."""
        return self.retrieval_service.retrieve(
            query=query,
            top_k=top_k,
        )