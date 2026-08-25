"""Grounded Chat Skill — Answer questions using Lenny's knowledge base."""

from datetime import datetime
from typing import Any
from uuid import UUID

import structlog

from app.agents.models import AgentEventType, AgentEvent
from app.llm.base import LLMProvider
from app.rag.service import RAGService
from app.retrieval.service import RetrievalService


logger = structlog.get_logger(__name__)


class GroundedChatSkill:
    """
    Skill for answering product and growth questions grounded in
    Lenny's transcript knowledge base.

    This is the core RAG-based Q&A capability of the application.
    """

    def __init__(
        self,
        retrieval_service: RetrievalService,
        llm_provider: LLMProvider,
    ) -> None:
        self.rag_service = RAGService(
            retrieval_service=retrieval_service,
            llm_provider=llm_provider,
        )

    async def execute(
        self,
        session_id: UUID,
        prompt: str,
        conversation_history: list[dict[str, str]] | None = None,
        top_k: int = 5,
        events: list[AgentEvent] | None = None,
        agent_run_id: UUID | None = None,
    ) -> dict[str, Any]:
        """
        Execute grounded Q&A on the prompt.

        Args:
            session_id: Chat session ID
            prompt: User question
            conversation_history: Previous conversation
            top_k: Number of retrieved chunks
            events: Event list to populate
            agent_run_id: ID of the agent run

        Returns:
            dict with "response", "sources", "model", "provider"
        """

        if events is None:
            events = []

        # ---------------------------------------------------------
        # Event: Retrieval started
        # ---------------------------------------------------------

        events.append(
            AgentEvent(
                event_type=AgentEventType.RETRIEVAL_STARTED,
                session_id=session_id,
                timestamp=datetime.utcnow(),
                agent_run_id=agent_run_id,
                metadata={"top_k": top_k},
            )
        )

        # ---------------------------------------------------------
        # Execute RAG pipeline
        # ---------------------------------------------------------

        result = await self.rag_service.answer(
            question=prompt,
            top_k=top_k,
            conversation_history=conversation_history,
        )

        # ---------------------------------------------------------
        # Event: Retrieval completed
        # ---------------------------------------------------------

        events.append(
            AgentEvent(
                event_type=AgentEventType.RETRIEVAL_COMPLETED,
                session_id=session_id,
                timestamp=datetime.utcnow(),
                agent_run_id=agent_run_id,
                metadata={
                    "documents_retrieved": len(result.sources),
                    "provider": result.provider,
                    "model": result.model,
                },
            )
        )

        # ---------------------------------------------------------
        # Event: LLM completed
        # ---------------------------------------------------------

        events.append(
            AgentEvent(
                event_type=AgentEventType.LLM_COMPLETED,
                session_id=session_id,
                timestamp=datetime.utcnow(),
                agent_run_id=agent_run_id,
                metadata={
                    "provider": result.provider,
                    "model": result.model,
                    "response_length": len(result.response),
                },
            )
        )

        logger.info(
            "grounded_chat_skill_executed",
            session_id=str(session_id),
            sources_count=len(result.sources),
        )

        return {
            "response": result.response,
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
            "model": result.model,
            "provider": result.provider,
        }