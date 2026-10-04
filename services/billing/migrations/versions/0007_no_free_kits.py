"""no free kits: kits are paid when their topics are approved

Revision ID: 0007
Revises: 0006
Create Date: 2026-10-04
"""

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("wallets", "free_kits")


def downgrade() -> None:
    op.add_column(
        "wallets", sa.Column("free_kits", sa.Integer(), nullable=False, server_default="0")
    )
