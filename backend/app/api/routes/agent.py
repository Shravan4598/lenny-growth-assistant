import uuid
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.agents.agent import Agent
from app.core.config import Settings, get_settings
from app.db.models import (
    AgentEvent as DBAgentEvent,
    AgentRun as DBAgentRun,
    Artifact as DBArtifact,
    ChatSession,
)
from app.db.session import get_db
from app.llm.factory import create_llm_provider
from app.retrieval.service import RetrievalService


router = APIRouter()


# ============================================================
# Dependencies
# ============================================================


def get_llm(
    settings: Settings = Depends(get_settings),
):
    """
    Create the configured LLM provider.
    """
    return create_llm_provider(settings)


def get_retrieval(
    settings: Settings = Depends(get_settings),
) -> RetrievalService:
    """
    Create and initialize the retrieval service.

    The FAISS index must load successfully before the agent
    is allowed to execute.
    """

    service = RetrievalService(
        index_path=settings.retrieval_index_path,
        min_score=settings.retrieval_min_score,
    )

    service.load()

    return service


# ============================================================
# Request model
# ============================================================


class AgentRequest(BaseModel):
    session_id: uuid.UUID = Field(...)

    prompt: str = Field(
        ...,
        min_length=1,
    )

    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list
    )


# ============================================================
# Run agent
# ============================================================


@router.post("/run")
async def run_agent(
    request: AgentRequest,
    db: Session = Depends(get_db),
    llm=Depends(get_llm),
    retrieval_service: RetrievalService = Depends(get_retrieval),
):
    """
    Execute the agent, persist the run/events, and optionally
    create an artifact.
    """

    # --------------------------------------------------------
    # Validate session
    # --------------------------------------------------------

    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == request.session_id)
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail=f"Session {request.session_id} not found.",
        )

    # --------------------------------------------------------
    # Create agent
    # --------------------------------------------------------

    agent = Agent(
        retrieval_service=retrieval_service,
        llm_provider=llm,
    )

    try:

        # ====================================================
        # Execute agent
        # ====================================================

        agent_run = await agent.run(
            session_id=request.session_id,
            prompt=request.prompt,
            conversation_history=request.conversation_history,
        )

        # ====================================================
        # Persist AgentRun
        # ====================================================

        db_run = DBAgentRun(
            id=agent_run.id,
            session_id=agent_run.session_id,
            skill=agent_run.skill,
            status=agent_run.status,
            completed_at=agent_run.completed_at,
        )

        db.add(db_run)

        # ====================================================
        # Persist Agent Events
        # ====================================================

        for event in agent_run.events or []:

            db_event = DBAgentEvent(
                id=uuid.uuid4(),
                run_id=event.agent_run_id,
                event_type=event.event_type.value,
                metadata_json=event.metadata,
                timestamp=event.timestamp,
            )

            db.add(db_event)

        # ====================================================
        # Persist Artifact
        # ====================================================

        artifact_id = None

        if agent_run.skill in {
            "ship30",
            "artifact",
        }:

            artifact_id = uuid.uuid4()

            # ------------------------------------------------
            # Ship 30 Artifact
            # ------------------------------------------------

            if agent_run.skill == "ship30":

                title = "Ship 30 for 30 Essay"

                artifact_type = "ship30"

                artifact_metadata = {
                    "skill": "ship30",
                    "format": "markdown",
                    "description": (
                        "Approximately 1,250-word "
                        "Ship 30 for 30-style essay "
                        "grounded in Lenny's Podcast "
                        "and Newsletter knowledge."
                    ),
                }

            # ------------------------------------------------
            # Generic Artifact
            # ------------------------------------------------

            else:

                title = "Generated Document"

                artifact_type = "artifact"

                artifact_metadata = {
                    "skill": "artifact",
                    "format": "markdown",
                }

            # ------------------------------------------------
            # Create DB artifact
            # ------------------------------------------------

            db_artifact = DBArtifact(
                id=artifact_id,
                session_id=request.session_id,
                run_id=agent_run.id,
                artifact_type=artifact_type,
                title=title,
                content=agent_run.output,
                metadata_json=artifact_metadata,
            )

            db.add(db_artifact)

        # ====================================================
        # Commit transaction
        # ====================================================

        db.commit()

        # ====================================================
        # Response
        # ====================================================

        return {
            "response": (
                "Ship 30 for 30 essay generated successfully. "
                "Please view it in the Artifact Viewer."
                if agent_run.skill == "ship30"
                else (
                    "Artifact generated successfully. "
                    "Please view it in the side panel."
                    if artifact_id
                    else agent_run.output
                )
            ),

            "artifact_id": (
                str(artifact_id)
                if artifact_id
                else None
            ),

            "run_id": str(agent_run.id),

            "skill": agent_run.skill,

            "status": agent_run.status,
        }

    except HTTPException:

        db.rollback()

        raise

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(exc)}",
        ) from exc


# ============================================================
# Get agent run events
# ============================================================


@router.get("/runs/{run_id}/events")
def get_run_events(
    run_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """
    Retrieve events associated with an agent run.
    """

    # --------------------------------------------------------
    # Check that run exists
    # --------------------------------------------------------

    agent_run = (
        db.query(DBAgentRun)
        .filter(DBAgentRun.id == run_id)
        .first()
    )

    if agent_run is None:

        raise HTTPException(
            status_code=404,
            detail=f"Agent run {run_id} not found.",
        )

    # --------------------------------------------------------
    # Retrieve events
    # --------------------------------------------------------

    events = (
        db.query(DBAgentEvent)
        .filter(
            DBAgentEvent.run_id == run_id
        )
        .order_by(
            DBAgentEvent.timestamp
        )
        .all()
    )

    return [
        {
            "id": str(event.id),
            "run_id": str(event.run_id),
            "event_type": event.event_type,
            "timestamp": event.timestamp,
            "metadata": event.metadata_json,
        }
        for event in events
    ]