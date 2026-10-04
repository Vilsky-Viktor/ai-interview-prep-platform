"""kits are paid when their topics are approved, not up front; there are no free kits

Revision ID: 0009
Revises: 0008
Create Date: 2026-10-04
"""

import sqlalchemy as sa
from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("generations", "free_kit")
    # Generations already past review were paid up front, so they count as approved.
    op.add_column(
        "generations",
        sa.Column("approved", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.execute("UPDATE generations SET approved = true WHERE status <> 'awaiting_review'")


def downgrade() -> None:
    op.drop_column("generations", "approved")
    op.add_column(
        "generations",
        sa.Column("free_kit", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
