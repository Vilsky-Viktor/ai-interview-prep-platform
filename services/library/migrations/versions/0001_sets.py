"""sets, topics, questions

Revision ID: 0001
Revises:
Create Date: 2026-09-28
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
        "sets",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("owner_type", sa.String(32), nullable=False),
        sa.Column("owner_id", sa.String(128), nullable=False, index=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("source_text", sa.Text(), nullable=False),
        sa.Column("level", sa.String(32), nullable=False),
        sa.Column("requirements", postgresql.JSONB(), nullable=False),
        sa.Column("visibility", sa.String(32), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_table(
        "topics",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "set_id",
            sa.Uuid(),
            sa.ForeignKey("sets.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("subtopics", postgresql.JSONB(), nullable=False),
    )
    op.create_table(
        "questions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "topic_id",
            sa.Uuid(),
            sa.ForeignKey("topics.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("reference_answer", sa.Text(), nullable=False),
        sa.Column("options", postgresql.JSONB(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("questions")
    op.drop_table("topics")
    op.drop_table("sets")
