"""one credit balance, holds and gifts, instead of passes and packs

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-03
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("wallets", sa.Column("balance", sa.Integer(), nullable=False, server_default="0"))
    op.add_column(
        "wallets", sa.Column("reserved", sa.Integer(), nullable=False, server_default="0")
    )
    # Unused packs become credits: one preparation is 500, one candidate is 300. A pass still
    # running becomes 500 credits for each month it has left.
    op.execute(
        """
        UPDATE wallets SET balance =
            candidate_credits * 300
            + generation_credits * 500
            + CASE
                WHEN pass_until > now() THEN
                    500 * GREATEST(1, CEIL(EXTRACT(EPOCH FROM (pass_until - now())) / 86400 / 30))
                ELSE 0
              END
        """
    )
    op.drop_column("wallets", "candidate_credits")
    op.drop_column("wallets", "generation_credits")
    op.drop_column("wallets", "pass_until")
    op.drop_table("monthly_usage")
    op.create_table(
        "holds",
        sa.Column("key", sa.String(160), primary_key=True),
        sa.Column("owner_type", sa.String(16), nullable=False),
        sa.Column("owner_id", sa.String(128), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(64), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
    )
    op.create_table(
        "entries",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("key", sa.String(160), nullable=False),
        sa.Column("owner_type", sa.String(16), nullable=False),
        sa.Column("owner_id", sa.String(128), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(64), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_entries_owner_id", "entries", ["owner_id"])
    op.create_unique_constraint("uq_entries_key", "entries", ["key"])


def downgrade() -> None:
    op.drop_table("entries")
    op.drop_table("holds")
    op.create_table(
        "monthly_usage",
        sa.Column("user_id", sa.String(128), primary_key=True),
        sa.Column("month", sa.Date(), primary_key=True),
        sa.Column("free_generations", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "wallets",
        sa.Column("candidate_credits", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "wallets",
        sa.Column("generation_credits", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("wallets", sa.Column("pass_until", sa.DateTime(timezone=True), nullable=True))
    op.drop_column("wallets", "reserved")
    op.drop_column("wallets", "balance")
