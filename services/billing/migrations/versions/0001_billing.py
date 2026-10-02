"""wallets, monthly free usage and purchases

Revision ID: 0001
Revises:
Create Date: 2026-10-02
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "wallets",
        sa.Column("owner_type", sa.String(16), primary_key=True),
        sa.Column("owner_id", sa.String(128), primary_key=True),
        sa.Column("candidate_credits", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("generation_credits", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pass_until", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "monthly_usage",
        sa.Column("user_id", sa.String(128), primary_key=True),
        sa.Column("month", sa.Date(), primary_key=True),
        sa.Column("free_generations", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_table(
        "purchases",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("transaction_id", sa.String(64), nullable=False),
        sa.Column("product", sa.String(64), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("owner_type", sa.String(16), nullable=False),
        sa.Column("owner_id", sa.String(128), nullable=False),
        sa.Column("buyer_id", sa.String(128), nullable=True),
        sa.Column("total", sa.Text(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_purchases_transaction_id", "purchases", ["transaction_id"])
    op.create_index("ix_purchases_owner_id", "purchases", ["owner_id"])
    # A transaction grants each of its products once, however often Paddle retries the webhook.
    op.create_unique_constraint(
        "uq_purchases_transaction_product", "purchases", ["transaction_id", "product"]
    )


def downgrade() -> None:
    op.drop_table("purchases")
    op.drop_table("monthly_usage")
    op.drop_table("wallets")
