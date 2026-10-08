"""ats_candidates: when results were last kept, so the recovery job tries the longest kept first.

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ats_candidates", sa.Column("kept_at", sa.DateTime(timezone=True)))
    op.execute("UPDATE ats_candidates SET kept_at = created_at WHERE result IS NOT NULL")


def downgrade() -> None:
    op.drop_column("ats_candidates", "kept_at")
