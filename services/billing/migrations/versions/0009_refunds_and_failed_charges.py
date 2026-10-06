"""the top-up that paid a referral, so its refund takes the reward back; when an automatic
top-up's charge last failed, so a declined card isn't retried every few minutes

Revision ID: 0009
Revises: 0008
Create Date: 2026-10-06
"""

import sqlalchemy as sa
from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("referrals", sa.Column("rewarded_by", sa.String(64), nullable=True))
    op.create_index("ix_referrals_rewarded_by", "referrals", ["rewarded_by"])
    op.add_column("auto_top_ups", sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("auto_top_ups", "failed_at")
    op.drop_index("ix_referrals_rewarded_by", "referrals")
    op.drop_column("referrals", "rewarded_by")
