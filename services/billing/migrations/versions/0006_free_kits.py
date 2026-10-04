"""free prep kits on wallets: a new learner's welcome gift

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-04
"""

import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Existing wallets already got their welcome credits, so none of them gets a free kit.
    op.add_column(
        "wallets", sa.Column("free_kits", sa.Integer(), nullable=False, server_default="0")
    )


def downgrade() -> None:
    op.drop_column("wallets", "free_kits")
