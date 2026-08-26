"""Add updated_at to artifacts.

Revision ID: 004_add_artifact_updated_at
Revises: 003_add_artifact_run_id
Create Date: 2026-08-26
"""

from alembic import op
import sqlalchemy as sa


# ============================================================
# Revision identifiers
# ============================================================

revision = "004_add_artifact_updated_at"
down_revision = "003_add_artifact_run_id"
branch_labels = None
depends_on = None


# ============================================================
# Upgrade
# ============================================================

def upgrade() -> None:
    """
    Add updated_at column to artifacts.

    Existing artifact rows receive the current timestamp.
    """

    op.add_column(
        "artifacts",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )


# ============================================================
# Downgrade
# ============================================================

def downgrade() -> None:
    """
    Remove updated_at from artifacts.
    """

    op.drop_column(
        "artifacts",
        "updated_at",
    )