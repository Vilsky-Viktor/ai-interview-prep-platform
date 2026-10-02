"""answer statistics per question, and revisions kept when a question is replaced

Revision ID: 0009
Revises: 0008
Create Date: 2026-10-01
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def question_fk(**kwargs) -> sa.Column:
    return sa.Column(
        "question_id",
        sa.Uuid(),
        sa.ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        **kwargs,
    )


def upgrade() -> None:
    op.create_table(
        "question_stats",
        question_fk(primary_key=True),
        sa.Column("answers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("correct", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "option_picks", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'")
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "question_revisions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        question_fk(index=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("options", postgresql.JSONB(), nullable=False),
        sa.Column("answers", sa.Integer(), nullable=False),
        sa.Column("correct", sa.Integer(), nullable=False),
        sa.Column("option_picks", postgresql.JSONB(), nullable=False),
        sa.Column("likes", sa.Integer(), nullable=False),
        sa.Column("dislikes", sa.Integer(), nullable=False),
        sa.Column("reports", postgresql.JSONB(), nullable=False),
        sa.Column("replaced_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("question_revisions")
    op.drop_table("question_stats")
