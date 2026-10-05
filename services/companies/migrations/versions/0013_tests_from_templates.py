"""a test made from a template has no generation

Revision ID: 0013
Revises: 0012
Create Date: 2026-10-05
"""

import sqlalchemy as sa
from alembic import op

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("interviews", "generation_id", existing_type=sa.Uuid(), nullable=True)


def downgrade() -> None:
    op.execute("DELETE FROM interviews WHERE generation_id IS NULL")
    op.alter_column("interviews", "generation_id", existing_type=sa.Uuid(), nullable=False)
