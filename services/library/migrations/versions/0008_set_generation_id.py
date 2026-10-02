"""sets remember the generation that produced them, so a retried save returns the same set

Revision ID: 0008
Revises: 0007
Create Date: 2026-10-01
"""

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sets", sa.Column("generation_id", sa.Uuid(), nullable=True))
    op.create_unique_constraint("uq_sets_generation_id", "sets", ["generation_id"])


def downgrade() -> None:
    op.drop_constraint("uq_sets_generation_id", "sets", type_="unique")
    op.drop_column("sets", "generation_id")
