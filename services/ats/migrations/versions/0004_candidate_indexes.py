"""ats_candidates: indexes on email and created_at.

By email: a user's data (export, deletion) and a candidate the company erased. By created_at:
candidates past their retention period, and a top-up's recent ones.

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-08
"""

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_ats_candidates_email", "ats_candidates", ["email"])
    op.create_index("ix_ats_candidates_created_at", "ats_candidates", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_ats_candidates_created_at", "ats_candidates")
    op.drop_index("ix_ats_candidates_email", "ats_candidates")
