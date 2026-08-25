from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.sessions import (
    CreateSessionRequest,
    SessionDetailResponse,
    SessionMessageResponse,
    SessionResponse,
)
from app.api.services.session_service import SessionService
from app.db.session import get_db


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)


def get_session_service(
    db: Session = Depends(get_db),
) -> SessionService:
    return SessionService(db)


@router.post(
    "",
    response_model=SessionResponse,
)
def create_session(
    request: CreateSessionRequest,
    service: SessionService = Depends(get_session_service),
) -> SessionResponse:
    session = service.create_session(
        title=request.title,
        user_metadata=request.user_metadata,
    )

    return SessionResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.get(
    "",
    response_model=list[SessionResponse],
)
def list_sessions(
    service: SessionService = Depends(get_session_service),
) -> list[SessionResponse]:
    sessions = service.list_sessions()

    return [
        SessionResponse(
            id=session.id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )
        for session in sessions
    ]


@router.get(
    "/{session_id}",
    response_model=SessionDetailResponse,
)
def get_session(
    session_id: UUID,
    service: SessionService = Depends(get_session_service),
) -> SessionDetailResponse:
    session = service.get_session(session_id)

    messages = service.get_messages(
        session_id,
    )

    return SessionDetailResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=[
            SessionMessageResponse(
                id=message.id,
                role=message.role,
                content=message.content,
                created_at=message.created_at,
            )
            for message in messages
        ],
    )