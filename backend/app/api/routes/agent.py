import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.db.models import AgentRun as DBAgentRun, AgentEvent as DBAgentEvent, Artifact as DBArtifact
from app.agents.agent import Agent
from app.llm.factory import get_llm
from app.retrieval.service import RetrievalService
from app.retrieval.vector_store import FAISSVectorStore

router = APIRouter()

class AgentRequest(BaseModel):
    session_id: uuid.UUID
    prompt: str
    conversation_history: List[Dict[str, str]] = []

@router.post("/run")
async def run_agent(request: AgentRequest, db: Session = Depends(get_db)):
    llm = get_llm()
    # Replace with how your RetrievalService is actually initialized in your project
    vector_store = FAISSVectorStore() 
    retrieval_service = RetrievalService(vector_store)
    
    agent = Agent(retrieval_service=retrieval_service, llm_provider=llm)
    
    try:
        agent_run = await agent.run(
            session_id=request.session_id, 
            prompt=request.prompt,
            conversation_history=request.conversation_history
        )
        
        # Save run
        db_run = DBAgentRun(
            id=str(agent_run.id),
            session_id=str(agent_run.session_id),
            skill=agent_run.skill,
            status=agent_run.status,
            completed_at=agent_run.completed_at
        )
        db.add(db_run)
        
        # Save events
        for event in (agent_run.events or []):
            db.add(DBAgentEvent(
                id=str(uuid.uuid4()),
                run_id=str(event.agent_run_id),
                event_type=event.event_type.value,
                metadata_=event.metadata,
                timestamp=event.timestamp
            ))
            
        # Save Artifact if generated
        artifact_id = None
        if agent_run.skill in ["ship30", "artifact"]:
            artifact_id = str(uuid.uuid4())
            title = "30-Day Execution Plan" if agent_run.skill == "ship30" else "Generated Document"
            db.add(DBArtifact(
                id=artifact_id,
                session_id=str(request.session_id),
                run_id=str(agent_run.id),
                artifact_type=agent_run.skill,
                title=title,
                content=agent_run.output
            ))
            
        db.commit()
        
        return {
            "response": "Artifact generated. See viewer." if artifact_id else agent_run.output,
            "artifact_id": artifact_id,
            "run_id": str(agent_run.id)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/runs/{run_id}/events")
def get_run_events(run_id: str, db: Session = Depends(get_db)):
    events = db.query(DBAgentEvent).filter(DBAgentEvent.run_id == run_id).order_by(DBAgentEvent.timestamp).all()
    return [{"event_type": e.event_type, "timestamp": e.timestamp, "metadata": e.metadata_} for e in events]