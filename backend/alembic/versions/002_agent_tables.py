"""Add agent run and event tables.

Revision ID: 002_agent_tables
Revises: 001_initial_schema
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "002_agent_tables"

down_revision: Union[str, None] = "001_initial_schema"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create agent_runs and agent_events tables."""

    op.create_table(
        "agent_runs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "skill",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="running",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["sessions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_agent_runs_session_id",
        "agent_runs",
        ["session_id"],
    )

    op.create_table(
        "agent_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "run_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "event_type",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "metadata_json",
            sa.JSON(),
            nullable=True,
        ),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["agent_runs.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_agent_events_run_id",
        "agent_events",
        ["run_id"],
    )


def downgrade() -> None:
    """Remove agent_events and agent_runs tables."""

    op.drop_index(
        "ix_agent_events_run_id",
        table_name="agent_events",
    )

    op.drop_table("agent_events")

    op.drop_index(
        "ix_agent_runs_session_id",
        table_name="agent_runs",
    )

    op.drop_table("agent_runs")