import uuid
from typing import List, Dict, Any
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.db.models import AgentRun as DBAgentRun, AgentEvent as DBAgentEvent, Artifact as DBArtifact
from app.agents.agent import Agent

# Import the actual factories and services from your project
from app.core.config import Settings
from app.llm.factory import create_llm_provider
from app.retrieval.service import RetrievalService

router = APIRouter()

# --- Dependency Injection Setup ---

def get_settings() -> Settings:
    """Provide the application settings."""
    return Settings()

def get_llm(settings: Settings = Depends(get_settings)):
    """Provide the configured LLM."""
    return create_llm_provider(settings)

def get_retrieval(settings: Settings = Depends(get_settings)):
    """Provide the RetrievalService and load the FAISS index."""
    # Look for the index path in settings, default to data/processed
    index_path = getattr(settings, "faiss_index_path", Path("data/processed/faiss_index"))
    
    service = RetrievalService(index_path=index_path)
    try:
        service.load()
    except Exception:
        # If the index isn't built yet, we still return the service. 
        # The agent/RAG pipeline will handle the empty state gracefully.
        pass
        
    return service

# --- API Models ---

class AgentRequest(BaseModel):
    session_id: uuid.UUID
    prompt: str
    conversation_history: List[Dict[str, str]] = []

# --- Routes ---

@router.post("/run")
async def run_agent(
    request: AgentRequest, 
    db: Session = Depends(get_db),
    llm = Depends(get_llm),
    retrieval_service: RetrievalService = Depends(get_retrieval)
):
    """Execute the agent loop, persist the run, and store artifacts."""
    
    agent = Agent(retrieval_service=retrieval_service, llm_provider=llm)
    
    try:
        # Execute domain logic
        agent_run = await agent.run(
            session_id=request.session_id, 
            prompt=request.prompt,
            conversation_history=request.conversation_history
        )
        
        # Persist AgentRun (Using native UUIDs)
        db_run = DBAgentRun(
            id=agent_run.id,
            session_id=agent_run.session_id,
            skill=agent_run.skill,
            status=agent_run.status,
            completed_at=agent_run.completed_at
        )
        db.add(db_run)
        
        # Persist Transcripts (Events)
        for event in (agent_run.events or []):
            db.add(DBAgentEvent(
                id=uuid.uuid4(),
                run_id=event.agent_run_id,
                event_type=event.event_type.value,
                metadata_json=event.metadata,
                timestamp=event.timestamp
            ))
            
        # Save Artifact if the agent generated one
        artifact_id = None
        if agent_run.skill in ["ship30", "artifact"]:
            artifact_id = uuid.uuid4()
            title = "30-Day Execution Plan" if agent_run.skill == "ship30" else "Generated Document"
            
            db.add(DBArtifact(
                id=artifact_id,
                session_id=request.session_id,
                run_id=agent_run.id,
                artifact_type=agent_run.skill,
                title=title,
                content=agent_run.output,
                metadata_json={}
            ))
            
        db.commit()
        
        return {
            "response": "Artifact generated successfully. Please view it in the side panel." if artifact_id else agent_run.output,
            "artifact_id": str(artifact_id) if artifact_id else None,
            "run_id": str(agent_run.id)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/runs/{run_id}/events")
def get_run_events(run_id: uuid.UUID, db: Session = Depends(get_db)):
    """Retrieve the transcript events for a specific agent execution."""
    events = db.query(DBAgentEvent).filter(DBAgentEvent.run_id == run_id).order_by(DBAgentEvent.timestamp).all()
    return [{"event_type": e.event_type, "timestamp": e.timestamp, "metadata": e.metadata_json} for e in events]