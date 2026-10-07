"""slack_connections: each company's Slack channel for its notifications

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "slack_connections",
        sa.Column("company_id", sa.String(128), primary_key=True),
        sa.Column("team", sa.String(200), nullable=False),
        sa.Column("channel", sa.String(200), nullable=False),
        sa.Column("webhook", sa.Text(), nullable=False),
        sa.Column("token", sa.Text(), nullable=False),
        sa.Column("kinds", JSONB(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_by", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("slack_connections")
