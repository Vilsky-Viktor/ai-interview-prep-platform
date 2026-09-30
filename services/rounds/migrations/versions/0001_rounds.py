"""rounds, answers

Revision ID: 0001
Revises:
Create Date: 2026-09-29
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rounds",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.String(128), nullable=False, index=True),
        sa.Column("topic_id", sa.Uuid(), nullable=False, index=True),
        sa.Column("preparation_id", sa.Uuid(), nullable=False),
        sa.Column("topic_title", sa.Text(), nullable=False),
        sa.Column("mode", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("questions", postgresql.JSONB(), nullable=False),
        sa.Column("final_score", sa.Integer()),
        sa.Column(
            "started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "answers",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "round_id",
            sa.Uuid(),
            sa.ForeignKey("rounds.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("text", sa.Text()),
        sa.Column("option_index", sa.Integer()),
        sa.Column("correct", sa.Boolean()),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("feedback", sa.Text()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint("round_id", "question_id"),
    )


def downgrade() -> None:
    op.drop_table("answers")
    op.drop_table("rounds")
