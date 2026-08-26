"""Add run_id to artifacts.

Revision ID: 003_add_artifact_run_id
Revises: 002_agent_tables
Create Date: 2026-08-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect


# ============================================================
# Revision identifiers
# ============================================================

revision = "003_add_artifact_run_id"
down_revision = "002_agent_tables"
branch_labels = None
depends_on = None


# ============================================================
# Upgrade
# ============================================================

def upgrade() -> None:
    """
    Safely add run_id to artifacts.

    The database may already contain sanitized_content, so this
    migration checks the existing schema before modifying it.
    """

    bind = op.get_bind()
    inspector = inspect(bind)

    # --------------------------------------------------------
    # Inspect existing artifacts columns
    # --------------------------------------------------------

    columns = {
        column["name"]
        for column in inspector.get_columns("artifacts")
    }

    # --------------------------------------------------------
    # Add run_id only if it does not already exist
    # --------------------------------------------------------

    if "run_id" not in columns:
        op.add_column(
            "artifacts",
            sa.Column(
                "run_id",
                postgresql.UUID(as_uuid=True),
                nullable=True,
            ),
        )

    # Refresh inspector after adding column
    inspector = inspect(bind)

    # --------------------------------------------------------
    # Add foreign key only if it does not already exist
    # --------------------------------------------------------

    foreign_keys = inspector.get_foreign_keys("artifacts")

    run_id_fk_exists = any(
        fk.get("name") == "fk_artifacts_run_id_agent_runs"
        for fk in foreign_keys
    )

    if not run_id_fk_exists:
        op.create_foreign_key(
            "fk_artifacts_run_id_agent_runs",
            "artifacts",
            "agent_runs",
            ["run_id"],
            ["id"],
            ondelete="SET NULL",
        )

    # --------------------------------------------------------
    # Add index only if it does not already exist
    # --------------------------------------------------------

    indexes = inspector.get_indexes("artifacts")

    run_id_index_exists = any(
        index.get("name") == "ix_artifacts_run_id"
        for index in indexes
    )

    if not run_id_index_exists:
        op.create_index(
            "ix_artifacts_run_id",
            "artifacts",
            ["run_id"],
            unique=False,
        )


# ============================================================
# Downgrade
# ============================================================

def downgrade() -> None:
    """
    Safely remove run_id from artifacts.
    """

    bind = op.get_bind()
    inspector = inspect(bind)

    # --------------------------------------------------------
    # Remove index if it exists
    # --------------------------------------------------------

    indexes = inspector.get_indexes("artifacts")

    if any(
        index.get("name") == "ix_artifacts_run_id"
        for index in indexes
    ):
        op.drop_index(
            "ix_artifacts_run_id",
            table_name="artifacts",
        )

    # --------------------------------------------------------
    # Remove foreign key if it exists
    # --------------------------------------------------------

    foreign_keys = inspector.get_foreign_keys("artifacts")

    if any(
        fk.get("name") == "fk_artifacts_run_id_agent_runs"
        for fk in foreign_keys
    ):
        op.drop_constraint(
            "fk_artifacts_run_id_agent_runs",
            "artifacts",
            type_="foreignkey",
        )

    # --------------------------------------------------------
    # Remove run_id if it exists
    # --------------------------------------------------------

    columns = {
        column["name"]
        for column in inspector.get_columns("artifacts")
    }

    if "run_id" in columns:
        op.drop_column(
            "artifacts",
            "run_id",
        )