"""api: companies' API keys (as hashes), their web hooks (secrets encrypted), and which events
each web hook got. Companies live in the companies service: their ids are plain columns.

Revision ID: 0001
Revises:
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "api_keys",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("shown", sa.String(20), nullable=False),
        sa.Column("hash", sa.String(64), nullable=False, unique=True),
        sa.Column("created_by", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("last_used_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_api_keys_company_id", "api_keys", ["company_id"])
    op.create_index("ix_api_keys_created_by", "api_keys", ["created_by"])
    op.create_table(
        "webhooks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("secret", sa.Text(), nullable=False),
        sa.Column("created_by", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_webhooks_company_id", "webhooks", ["company_id"])
    op.create_index("ix_webhooks_created_by", "webhooks", ["created_by"])
    op.create_table(
        "webhook_deliveries",
        sa.Column(
            "webhook_id",
            sa.Uuid(),
            sa.ForeignKey("webhooks.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("event_id", sa.String(128), primary_key=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("webhook_deliveries")
    op.drop_table("webhooks")
    op.drop_table("api_keys")
