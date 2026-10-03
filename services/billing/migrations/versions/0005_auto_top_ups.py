"""automatic top-ups: a saved card's subscription and when to charge it

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-03
"""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auto_top_ups",
        sa.Column("owner_type", sa.String(16), primary_key=True),
        sa.Column("owner_id", sa.String(128), primary_key=True),
        sa.Column("product", sa.String(64), nullable=False),
        sa.Column("threshold", sa.Integer(), nullable=False),
        sa.Column("buyer_id", sa.String(128), nullable=False),
        sa.Column("subscription_id", sa.String(64), nullable=True, unique=True),
        sa.Column("charged_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("auto_top_ups")
