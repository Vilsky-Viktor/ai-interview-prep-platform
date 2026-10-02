"""integrity signals per question instead of counters per section

Revision ID: 0012
Revises: 0011
Create Date: 2026-10-02
"""

import sqlalchemy as sa
from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "signals",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "session_id",
            sa.Uuid(),
            sa.ForeignKey("sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("question_id", sa.Uuid(), nullable=True),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_signals_session_id", "signals", ["session_id"])
    op.drop_column("sessions", "copies")
    op.drop_column("sessions", "tab_leaves")


def downgrade() -> None:
    op.add_column(
        "sessions", sa.Column("tab_leaves", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column("sessions", sa.Column("copies", sa.Integer(), nullable=False, server_default="0"))
    op.drop_index("ix_signals_session_id", "signals")
    op.drop_table("signals")
