"""generation kind and company

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
    op.add_column(
        "generations",
        sa.Column("kind", sa.String(32), nullable=False, server_default="preparation"),
    )
    op.add_column("generations", sa.Column("company_id", sa.Uuid()))


def downgrade() -> None:
    op.drop_column("generations", "company_id")
    op.drop_column("generations", "kind")
