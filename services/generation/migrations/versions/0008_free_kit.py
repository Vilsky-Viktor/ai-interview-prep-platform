"""whether a generation is the learner's free kit

Revision ID: 0008
Revises: 0007
Create Date: 2026-10-04
"""

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "generations",
        sa.Column("free_kit", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("generations", "free_kit")
