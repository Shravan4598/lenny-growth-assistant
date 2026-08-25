"""Ship 30 Skill — Generate a 30-day writing/execution plan."""

from datetime import datetime
from typing import Any
from uuid import UUID

import structlog

from app.agents.models import AgentEventType, AgentEvent
from app.core.exceptions import AppError
from app.llm.base import LLMProvider
from app.rag.prompts import build_ship30_prompt
from app.retrieval.service import RetrievalService


logger = structlog.get_logger(__name__)


class Ship30Skill:
    """
    Skill for generating a structured 30-day writing/execution plan.

    The output is a detailed daily breakdown with objectives,
    actions, and deliverables grounded in Lenny's knowledge.
    """

    # Maximum number of daily entries to validate
    EXPECTED_DAYS = 30

    # Maximum output tokens for the plan
    MAX_OUTPUT_TOKENS = 2000

    def __init__(
        self,
        retrieval_service: RetrievalService,
        llm_provider: LLMProvider,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.llm_provider = llm_provider

    async def execute(
        self,
        session_id: UUID,
        prompt: str,
        conversation_history: list[dict[str, str]] | None = None,
        events: list[AgentEvent] | None = None,
        agent_run_id: UUID | None = None,
    ) -> dict[str, Any]:
        """
        Generate a Ship 30 plan.

        Args:
            session_id: Chat session ID
            prompt: User request for the plan
            conversation_history: Previous conversation
            events: Event list to populate
            agent_run_id: ID of the agent run

        Returns:
            dict with "response" (markdown plan) and "sources"
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
                metadata={"query": "Ship 30 plan generation"},
            )
        )

        # ---------------------------------------------------------
        # Retrieve relevant knowledge
        # ---------------------------------------------------------

        try:
            retrieved_chunks = self.retrieval_service.retrieve(
                query=prompt,
                top_k=10,
            )

        except Exception as exc:
            logger.warning(
                "ship30_retrieval_failed",
                error=str(exc),
            )
            retrieved_chunks = []

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
                    "documents_retrieved": len(retrieved_chunks),
                },
            )
        )

        # ---------------------------------------------------------
        # Build context from retrieved chunks
        # ---------------------------------------------------------

        context = self._build_context(retrieved_chunks)

        # ---------------------------------------------------------
        # Build structured prompt
        # ---------------------------------------------------------

        shipping_prompt = build_ship30_prompt(
            topic=prompt,
            context=context,
            conversation_history=self._format_history(
                conversation_history
            ),
        )

        # ---------------------------------------------------------
        # Event: LLM started
        # ---------------------------------------------------------

        events.append(
            AgentEvent(
                event_type=AgentEventType.LLM_STARTED,
                session_id=session_id,
                timestamp=datetime.utcnow(),
                agent_run_id=agent_run_id,
                metadata={"model": self.llm_provider.model_name},
            )
        )

        # ---------------------------------------------------------
        # Generate plan
        # ---------------------------------------------------------

        try:
            result = await self.llm_provider.generate(
                shipping_prompt,
                temperature=0.3,
                max_tokens=self.MAX_OUTPUT_TOKENS,
            )

        except Exception as exc:
            logger.error(
                "ship30_generation_failed",
                error=str(exc),
            )

            raise AppError(
                status_code=500,
                code="SHIP30_GENERATION_FAILED",
                message="Failed to generate Ship 30 plan.",
            ) from exc

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
                    "model": result.model,
                    "provider": result.provider,
                    "response_length": len(result.content),
                },
            )
        )

        # ---------------------------------------------------------
        # Event: Artifact created
        # ---------------------------------------------------------

        events.append(
            AgentEvent(
                event_type=AgentEventType.ARTIFACT_CREATED,
                session_id=session_id,
                timestamp=datetime.utcnow(),
                agent_run_id=agent_run_id,
                metadata={
                    "artifact_type": "ship30",
                    "title": f"Ship 30: {prompt[:50]}",
                },
            )
        )

        logger.info(
            "ship30_skill_executed",
            session_id=str(session_id),
            sources_count=len(retrieved_chunks),
        )

        return {
            "response": result.content,
            "sources": [
                {
                    "chunk_id": chunk.chunk.chunk_id,
                    "title": chunk.chunk.title,
                    "guest": chunk.chunk.guest,
                    "date": chunk.chunk.date,
                    "source_url": chunk.chunk.source_url,
                    "score": chunk.score,
                }
                for chunk in retrieved_chunks
            ],
            "model": result.model,
            "provider": result.provider,
        }

    @staticmethod
    def _format_history(
        history: list[dict[str, str]] | None,
    ) -> str:
        """Format conversation history for the prompt."""

        if not history:
            return "No previous conversation."

        lines = []
        for msg in history:
            role = msg.get("role", "").capitalize()
            content = msg.get("content", "").strip()
            if content:
                lines.append(f"{role}: {content}")

        return "\n".join(lines) if lines else "No previous conversation."

    @staticmethod
    def _build_context(retrieved_chunks) -> str:
        """Build context from retrieved chunks."""

        if not retrieved_chunks:
            return (
                "No additional context available. "
                "Generate the plan based on general knowledge."
            )

        sections = []
        for i, item in enumerate(retrieved_chunks[:5], start=1):
            chunk = item.chunk
            text = chunk.text[:300]
            sections.append(
                f"Source {i}: {chunk.title}\n{text}..."
            )

        return "\n\n".join(sections)