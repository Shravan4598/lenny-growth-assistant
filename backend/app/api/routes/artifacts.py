from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Artifact as DBArtifact

router = APIRouter()

@router.get("/sessions/{session_id}")
def get_session_artifacts(session_id: str, db: Session = Depends(get_db)):
    return db.query(DBArtifact).filter(DBArtifact.session_id == session_id).all()

@router.get("/{artifact_id}")
def get_artifact(artifact_id: str, db: Session = Depends(get_db)):
    artifact = db.query(DBArtifact).filter(DBArtifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Not found")
    return artifact