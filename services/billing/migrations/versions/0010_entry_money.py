"""the money a top-up, refund or chargeback moved, and whether a top-up was automatic, on each
history entry; past top-ups get theirs from their purchases

Revision ID: 0010
Revises: 0009
Create Date: 2026-10-10
"""

import sqlalchemy as sa
from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("entries", sa.Column("total", sa.Text(), nullable=True))
    op.add_column("entries", sa.Column("currency", sa.String(3), nullable=True))
    op.add_column(
        "entries",
        sa.Column("automatic", sa.Boolean(), nullable=False, server_default="false"),
    )
    # A top-up's key is "{transaction_id}:{product}", one per purchase line.
    op.execute(
        """
        UPDATE entries SET total = purchases.total, currency = purchases.currency
        FROM purchases
        WHERE entries.reason = 'topup'
          AND entries.key = purchases.transaction_id || ':' || purchases.product
        """
    )


def downgrade() -> None:
    op.drop_column("entries", "automatic")
    op.drop_column("entries", "currency")
    op.drop_column("entries", "total")
