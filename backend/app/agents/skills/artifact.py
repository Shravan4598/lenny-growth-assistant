"""Artifact Generation Skill — Generate various document types."""

from datetime import datetime
from typing import Any
from uuid import UUID

import structlog

from app.agents.models import AgentEventType, AgentEvent
from app.core.exceptions import AppError
from app.llm.base import LLMProvider
from app.rag.prompts import build_artifact_prompt
from app.retrieval.service import RetrievalService


logger = structlog.get_logger(__name__)


class ArtifactGenerationSkill:
    """
    Skill for generating various artifact types including memos,
    frameworks, strategies, and HTML/CSS documents.
    """

    MAX_OUTPUT_TOKENS = 2500

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
        Generate an artifact.

        Args:
            session_id: Chat session ID
            prompt: Artifact generation request
            conversation_history: Previous conversation
            events: Event list to populate
            agent_run_id: ID of the agent run

        Returns:
            dict with "response" (artifact content) and "sources"
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
                metadata={"query": "Artifact generation context"},
            )
        )

        # ---------------------------------------------------------
        # Retrieve relevant knowledge
        # ---------------------------------------------------------

        try:
            retrieved_chunks = self.retrieval_service.retrieve(
                query=prompt,
                top_k=8,
            )

        except Exception as exc:
            logger.warning(
                "artifact_retrieval_failed",
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
        # Build context
        # ---------------------------------------------------------

        context = self._build_context(retrieved_chunks)

        # ---------------------------------------------------------
        # Determine artifact type from prompt
        # ---------------------------------------------------------

        artifact_type = self._determine_artifact_type(prompt)

        # ---------------------------------------------------------
        # Build prompt
        # ---------------------------------------------------------

        generation_prompt = build_artifact_prompt(
            request=prompt,
            artifact_type=artifact_type,
            context=context,
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
                metadata={
                    "model": self.llm_provider.model_name,
                    "artifact_type": artifact_type,
                },
            )
        )

        # ---------------------------------------------------------
        # Generate artifact
        # ---------------------------------------------------------

        try:
            result = await self.llm_provider.generate(
                generation_prompt,
                temperature=0.3,
                max_tokens=self.MAX_OUTPUT_TOKENS,
            )

        except Exception as exc:
            logger.error(
                "artifact_generation_failed",
                error=str(exc),
            )

            raise AppError(
                status_code=500,
                code="ARTIFACT_GENERATION_FAILED",
                message="Failed to generate artifact.",
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
                    "artifact_type": artifact_type,
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
                    "artifact_type": artifact_type,
                    "title": f"{artifact_type.title()}: {prompt[:40]}",
                },
            )
        )

        logger.info(
            "artifact_skill_executed",
            session_id=str(session_id),
            artifact_type=artifact_type,
            sources_count=len(retrieved_chunks),
        )

        return {
            "response": result.content,
            "artifact_type": artifact_type,
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
    def _determine_artifact_type(prompt: str) -> str:
        """Determine artifact type from the request."""

        prompt_lower = prompt.lower()

        if "html" in prompt_lower or "css" in prompt_lower:
            return "html"

        if "markdown" in prompt_lower:
            return "markdown"

        if "memo" in prompt_lower:
            return "markdown"

        if "framework" in prompt_lower:
            return "markdown"

        if "template" in prompt_lower:
            return "markdown"

        return "markdown"

    @staticmethod
    def _build_context(retrieved_chunks) -> str:
        """Build context from retrieved chunks."""

        if not retrieved_chunks:
            return (
                "No additional context available. "
                "Generate the artifact based on general knowledge."
            )

        sections = []
        for i, item in enumerate(retrieved_chunks[:5], start=1):
            chunk = item.chunk
            text = chunk.text[:250]
            sections.append(
                f"Reference {i}: {chunk.title}\n{text}..."
            )

        return "\n\n".join(sections)