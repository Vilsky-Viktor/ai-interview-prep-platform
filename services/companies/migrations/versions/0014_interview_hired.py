"""a company marks a test as hired: it's done

Revision ID: 0014
Revises: 0013
Create Date: 2026-10-05
"""

import sqlalchemy as sa
from alembic import op

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "interviews", sa.Column("hired", sa.Boolean(), nullable=False, server_default="false")
    )


def downgrade() -> None:
    op.drop_column("interviews", "hired")
