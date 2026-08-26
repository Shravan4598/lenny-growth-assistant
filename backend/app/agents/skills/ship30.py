"""Ship 30 Skill — Generate a grounded Ship 30 for 30-style essay."""

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
    Dedicated skill for generating a grounded Ship 30 for 30-style essay.

    The skill:
    1. Retrieves relevant Lenny content.
    2. Builds a structured writing prompt.
    3. Generates approximately 1,250 words.
    4. Returns source metadata.
    5. Emits agent lifecycle events.
    """

    # Approximately 1,250 words requires more than 2,000 tokens
    # in many cases, especially with Markdown headings.
    MAX_OUTPUT_TOKENS = 3000

    # Number of chunks used for retrieval.
    RETRIEVAL_TOP_K = 10

    # Number of retrieved chunks actually inserted into prompt.
    MAX_CONTEXT_CHUNKS = 7

    # Maximum characters taken from each chunk.
    MAX_CHARS_PER_CHUNK = 1500

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
        Generate a grounded Ship 30 for 30-style essay.

        Args:
            session_id:
                Chat session ID.

            prompt:
                User request for the Ship 30 essay.

            conversation_history:
                Previous messages in the session.

            events:
                Agent event list.

            agent_run_id:
                Current agent run ID.

        Returns:
            Dictionary containing generated response and sources.
        """

        if events is None:
            events = []

        # =====================================================
        # Retrieval started
        # =====================================================

        events.append(
            AgentEvent(
                event_type=AgentEventType.RETRIEVAL_STARTED,
                session_id=session_id,
                timestamp=datetime.utcnow(),
                agent_run_id=agent_run_id,
                metadata={
                    "query": prompt,
                    "skill": "ship30",
                },
            )
        )

        # =====================================================
        # Retrieve relevant Lenny knowledge
        # =====================================================

        try:
            retrieved_chunks = self.retrieval_service.retrieve(
                query=prompt,
                top_k=self.RETRIEVAL_TOP_K,
            )

        except Exception as exc:
            logger.warning(
                "ship30_retrieval_failed",
                session_id=str(session_id),
                error=str(exc),
            )

            retrieved_chunks = []

        # =====================================================
        # Retrieval completed
        # =====================================================

        events.append(
            AgentEvent(
                event_type=AgentEventType.RETRIEVAL_COMPLETED,
                session_id=session_id,
                timestamp=datetime.utcnow(),
                agent_run_id=agent_run_id,
                metadata={
                    "documents_retrieved": len(retrieved_chunks),
                    "skill": "ship30",
                },
            )
        )

        # =====================================================
        # Build context
        # =====================================================

        context = self._build_context(
            retrieved_chunks
        )

        # =====================================================
        # Build conversation history
        # =====================================================

        formatted_history = self._format_history(
            conversation_history
        )

        # =====================================================
        # Build Ship 30 prompt
        # =====================================================

        shipping_prompt = build_ship30_prompt(
            topic=prompt,
            context=context,
            conversation_history=formatted_history,
        )

        # =====================================================
        # LLM started
        # =====================================================

        events.append(
            AgentEvent(
                event_type=AgentEventType.LLM_STARTED,
                session_id=session_id,
                timestamp=datetime.utcnow(),
                agent_run_id=agent_run_id,
                metadata={
                    "model": self.llm_provider.model_name,
                    "skill": "ship30",
                },
            )
        )

        # =====================================================
        # Generate essay
        # =====================================================

        try:
            result = await self.llm_provider.generate(
                shipping_prompt,
                temperature=0.4,
                max_tokens=self.MAX_OUTPUT_TOKENS,
            )

        except Exception as exc:
            logger.error(
                "ship30_generation_failed",
                session_id=str(session_id),
                error=str(exc),
            )

            raise AppError(
                status_code=500,
                code="SHIP30_GENERATION_FAILED",
                message="Failed to generate Ship 30 essay.",
            ) from exc

        # =====================================================
        # LLM completed
        # =====================================================

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
                    "skill": "ship30",
                },
            )
        )

        # =====================================================
        # Artifact created
        # =====================================================

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
            model=result.model,
            provider=result.provider,
        )

        # =====================================================
        # Return result
        # =====================================================

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

    # =========================================================
    # Format history
    # =========================================================

    @staticmethod
    def _format_history(
        history: list[dict[str, str]] | None,
    ) -> str:
        """
        Format previous conversation into a compact text block.
        """

        if not history:
            return "No previous conversation."

        lines: list[str] = []

        for message in history:
            role = message.get(
                "role",
                "",
            ).capitalize()

            content = message.get(
                "content",
                "",
            ).strip()

            if content:
                lines.append(
                    f"{role}: {content}"
                )

        if not lines:
            return "No previous conversation."

        return "\n".join(lines)

    # =========================================================
    # Build retrieval context
    # =========================================================

    @classmethod
    def _build_context(
        cls,
        retrieved_chunks,
    ) -> str:
        """
        Convert retrieved chunks into grounded prompt context.
        """

        if not retrieved_chunks:
            return (
                "No relevant transcript context was retrieved. "
                "Do not invent Lenny-specific claims. "
                "State that the available material does not "
                "provide enough evidence."
            )

        sections: list[str] = []

        for index, item in enumerate(
            retrieved_chunks[: cls.MAX_CONTEXT_CHUNKS],
            start=1,
        ):
            chunk = item.chunk

            text = (
                chunk.text[: cls.MAX_CHARS_PER_CHUNK]
                .strip()
            )

            title = (
                chunk.title
                or "Untitled source"
            )

            guest = (
                chunk.guest
                or "Unknown guest"
            )

            date = (
                chunk.date
                or "Unknown date"
            )

            source_url = (
                chunk.source_url
                or "Unavailable"
            )

            sections.append(
                f"""Source {index}

Title: {title}
Guest: {guest}
Date: {date}
Source URL: {source_url}
Retrieval Score: {item.score:.3f}

Transcript Content:
{text}
"""
            )

        return "\n\n".join(sections)