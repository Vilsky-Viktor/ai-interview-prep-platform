"""chat messages, certificates

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-29
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "answer_id",
            sa.Uuid(),
            sa.ForeignKey("answers.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_table(
        "certificates",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.String(128), nullable=False, index=True),
        sa.Column("user_name", sa.Text(), nullable=False),
        sa.Column(
            "round_id",
            sa.Uuid(),
            sa.ForeignKey("rounds.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("topic_id", sa.Uuid(), nullable=False),
        sa.Column("topic_title", sa.Text(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column(
            "issued_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )


def downgrade() -> None:
    op.drop_table("certificates")
    op.drop_table("chat_messages")
