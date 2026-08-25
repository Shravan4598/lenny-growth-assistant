from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'agent_runs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('session_id', sa.String(), sa.ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('skill', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'agent_events',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('run_id', sa.String(), sa.ForeignKey('agent_runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('metadata_', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'artifacts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('session_id', sa.String(), sa.ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('run_id', sa.String(), sa.ForeignKey('agent_runs.id', ondelete='SET NULL'), nullable=True),
        sa.Column('artifact_type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('artifacts')
    op.drop_table('agent_events')
    op.drop_table('agent_runs')