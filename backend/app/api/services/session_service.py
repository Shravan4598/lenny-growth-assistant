from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.db.models import ChatSession, Message, User


class SessionService:
    """Application service for chat sessions and messages."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_session(
        self,
        title: str | None = None,
        user_metadata: dict | None = None,
    ) -> ChatSession:
        """Create a new independent chat session."""

        user = User(
            metadata_json=user_metadata or {},
        )

        self.db.add(user)
        self.db.flush()

        session = ChatSession(
            user_id=user.id,
            title=title,
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    def get_session(
        self,
        session_id: UUID,
    ) -> ChatSession:
        """Get a session or raise a 404 application error."""

        session = self.db.get(
            ChatSession,
            session_id,
        )

        if session is None:
            raise AppError(
                status_code=404,
                code="SESSION_NOT_FOUND",
                message="Chat session was not found.",
            )

        return session

    def list_sessions(self) -> list[ChatSession]:
        """Return all sessions ordered by most recently updated."""

        statement = (
            select(ChatSession)
            .order_by(ChatSession.updated_at.desc())
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_messages(
        self,
        session_id: UUID,
    ) -> list[Message]:
        """Return messages belonging only to this session."""

        self.get_session(session_id)

        statement = (
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
        )

        return list(
            self.db.scalars(statement).all()
        )

    def add_message(
        self,
        session_id: UUID,
        role: str,
        content: str,
        metadata: dict | None = None,
    ) -> Message:
        """Persist one conversation message and update session activity."""

        session = self.get_session(session_id)

        message = Message(
            session_id=session_id,
            role=role,
            content=content,
            metadata_json=metadata or {},
        )

        self.db.add(message)

        # Update the parent session's last activity timestamp.
        session.updated_at = func.now()

        self.db.commit()
        self.db.refresh(message)

        return message