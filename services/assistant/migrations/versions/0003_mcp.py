"""AI apps connected over MCP: the apps that registered and the users' connections to them

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-10
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
        "oauth_clients",
        sa.Column("client_id", sa.String(64), primary_key=True),
        sa.Column("info", JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "mcp_grants",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.String(128), nullable=False),
        sa.Column(
            "client_id",
            sa.String(64),
            sa.ForeignKey("oauth_clients.client_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("client_name", sa.String(80), nullable=False),
        sa.Column("redirect_host", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("access_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("access_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("refresh_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("refresh_expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_mcp_grants_user_id", "mcp_grants", ["user_id"])
    op.create_index("ix_mcp_grants_client_id", "mcp_grants", ["client_id"])
    op.create_index("ix_mcp_grants_refresh_expires_at", "mcp_grants", ["refresh_expires_at"])


def downgrade() -> None:
    op.drop_table("mcp_grants")
    op.drop_table("oauth_clients")
