"""Data models for agent execution and transcript events."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class AgentEventType(str, Enum):
    """Event types that can occur during agent execution."""

    AGENT_STARTED = "agent_started"
    PLANNING = "planning"
    RETRIEVAL_STARTED = "retrieval_started"
    RETRIEVAL_COMPLETED = "retrieval_completed"
    SKILL_STARTED = "skill_started"
    SKILL_COMPLETED = "skill_completed"
    ARTIFACT_CREATED = "artifact_created"
    LLM_STARTED = "llm_started"
    LLM_COMPLETED = "llm_completed"
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"


@dataclass
class AgentEvent:
    """Single event captured during agent execution."""

    event_type: AgentEventType
    session_id: UUID
    timestamp: datetime
    metadata: dict[str, Any]
    agent_run_id: UUID | None = None


@dataclass
class AgentRun:
    """Complete agent execution record."""

    id: UUID
    session_id: UUID
    skill: str
    input_prompt: str
    status: str  # "running", "completed", "failed"
    output: str | None = None
    error_message: str | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None
    events: list[AgentEvent] | None = None


class SkillType(str, Enum):
    """Available agent skills."""

    GROUNDED_CHAT = "grounded_chat"
    SHIP_30 = "ship30"
    ARTIFACT = "artifact"