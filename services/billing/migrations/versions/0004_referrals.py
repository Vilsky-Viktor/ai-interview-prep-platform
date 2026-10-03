"""referral codes on wallets, and who came through whose link

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-03
"""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("wallets", sa.Column("referral_code", sa.String(16), nullable=True))
    op.create_unique_constraint("wallets_referral_code_key", "wallets", ["referral_code"])
    op.create_table(
        "referrals",
        sa.Column("owner_type", sa.String(16), primary_key=True),
        sa.Column("owner_id", sa.String(128), primary_key=True),
        sa.Column("referrer_id", sa.String(128), nullable=False, index=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("rewarded_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("referrals")
    op.drop_constraint("wallets_referral_code_key", "wallets")
    op.drop_column("wallets", "referral_code")
