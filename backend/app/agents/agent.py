"""Core agent execution logic."""

import uuid
from datetime import datetime
from typing import Any

import structlog

from app.agents.models import AgentEventType, AgentRun, AgentEvent
from app.agents.router import determine_skill
from app.agents.skills.grounded_chat import GroundedChatSkill
from app.agents.skills.ship30 import Ship30Skill
from app.agents.skills.artifact import ArtifactGenerationSkill
from app.core.exceptions import AppError
from app.llm.base import LLMProvider
from app.retrieval.service import RetrievalService


logger = structlog.get_logger(__name__)


class Agent:
    """
    Agent orchestrator that routes user requests to appropriate skills.

    The agent coordinates:
    - Intent routing
    - Skill selection
    - Tool access
    - Event tracking
    - Artifact generation
    - Transcript persistence
    """

    def __init__(
        self,
        retrieval_service: RetrievalService,
        llm_provider: LLMProvider,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.llm_provider = llm_provider

        # Initialize skills
        self.grounded_chat_skill = GroundedChatSkill(
            retrieval_service=retrieval_service,
            llm_provider=llm_provider,
        )

        self.ship30_skill = Ship30Skill(
            retrieval_service=retrieval_service,
            llm_provider=llm_provider,
        )

        self.artifact_skill = ArtifactGenerationSkill(
            retrieval_service=retrieval_service,
            llm_provider=llm_provider,
        )

    async def run(
        self,
        session_id: uuid.UUID,
        prompt: str,
        conversation_history: list[dict[str, str]] | None = None,
        top_k: int = 5,
    ) -> AgentRun:
        """
        Execute the agent on a user prompt.

        Args:
            session_id: Chat session ID
            prompt: User input
            conversation_history: Previous messages in the conversation
            top_k: Number of retrieved documents

        Returns:
            AgentRun with execution details and transcript

        Raises:
            AppError: If skill execution fails
        """

        agent_run_id = uuid.uuid4()
        events: list[AgentEvent] = []

        # ---------------------------------------------------------
        # Event: Agent started
        # ---------------------------------------------------------

        events.append(
            AgentEvent(
                event_type=AgentEventType.AGENT_STARTED,
                session_id=session_id,
                timestamp=datetime.utcnow(),
                agent_run_id=agent_run_id,
                metadata={
                    "prompt": prompt[:500],  # Truncate for logging
                    "history_length": len(
                        conversation_history or []
                    ),
                },
            )
        )

        try:
            # ---------------------------------------------------------
            # Event: Planning
            # ---------------------------------------------------------

            skill = determine_skill(prompt)

            events.append(
                AgentEvent(
                    event_type=AgentEventType.PLANNING,
                    session_id=session_id,
                    timestamp=datetime.utcnow(),
                    agent_run_id=agent_run_id,
                    metadata={"selected_skill": skill},
                )
            )

            logger.info(
                "agent_routing",
                agent_run_id=str(agent_run_id),
                skill=skill,
                prompt_preview=prompt[:100],
            )

            # ---------------------------------------------------------
            # Execute selected skill
            # ---------------------------------------------------------

            if skill == "grounded_chat":
                result = await self.grounded_chat_skill.execute(
                    session_id=session_id,
                    prompt=prompt,
                    conversation_history=conversation_history,
                    top_k=top_k,
                    events=events,
                    agent_run_id=agent_run_id,
                )

            elif skill == "ship30":
                result = await self.ship30_skill.execute(
                    session_id=session_id,
                    prompt=prompt,
                    conversation_history=conversation_history,
                    events=events,
                    agent_run_id=agent_run_id,
                )

            elif skill == "artifact":
                result = await self.artifact_skill.execute(
                    session_id=session_id,
                    prompt=prompt,
                    conversation_history=conversation_history,
                    events=events,
                    agent_run_id=agent_run_id,
                )

            else:
                raise AppError(
                    status_code=500,
                    code="UNKNOWN_SKILL",
                    message=f"Unknown skill: {skill}",
                )

            # ---------------------------------------------------------
            # Event: Agent completed
            # ---------------------------------------------------------

            events.append(
                AgentEvent(
                    event_type=AgentEventType.AGENT_COMPLETED,
                    session_id=session_id,
                    timestamp=datetime.utcnow(),
                    agent_run_id=agent_run_id,
                    metadata={"skill": skill},
                )
            )

            logger.info(
                "agent_execution_completed",
                agent_run_id=str(agent_run_id),
                skill=skill,
            )

            return AgentRun(
                id=agent_run_id,
                session_id=session_id,
                skill=skill,
                input_prompt=prompt,
                status="completed",
                output=result.get("response", ""),
                created_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                events=events,
            )

        except AppError as exc:
            # ---------------------------------------------------------
            # Event: Agent failed
            # ---------------------------------------------------------

            events.append(
                AgentEvent(
                    event_type=AgentEventType.AGENT_FAILED,
                    session_id=session_id,
                    timestamp=datetime.utcnow(),
                    agent_run_id=agent_run_id,
                    metadata={
                        "error_code": exc.code,
                        "error_message": exc.message,
                    },
                )
            )

            logger.error(
                "agent_execution_failed",
                agent_run_id=str(agent_run_id),
                error=exc.code,
            )

            raise

        except Exception as exc:
            # ---------------------------------------------------------
            # Event: Unexpected failure
            # ---------------------------------------------------------

            events.append(
                AgentEvent(
                    event_type=AgentEventType.AGENT_FAILED,
                    session_id=session_id,
                    timestamp=datetime.utcnow(),
                    agent_run_id=agent_run_id,
                    metadata={
                        "error_type": type(exc).__name__,
                        "error_message": str(exc),
                    },
                )
            )

            logger.exception(
                "agent_execution_unexpected_error",
                agent_run_id=str(agent_run_id),
            )

            raise AppError(
                status_code=500,
                code="AGENT_EXECUTION_FAILED",
                message="Agent execution failed unexpectedly.",
            ) from exc