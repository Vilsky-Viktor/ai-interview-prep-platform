"""mcp_grants previous_refresh_hash and refreshed_at: a replaced refresh token used again well after
its refresh revokes the connection

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-14
"""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("mcp_grants", sa.Column("previous_refresh_hash", sa.String(64)))
    op.add_column("mcp_grants", sa.Column("refreshed_at", sa.DateTime(timezone=True)))
    op.create_index("ix_mcp_grants_previous_refresh_hash", "mcp_grants", ["previous_refresh_hash"])


def downgrade() -> None:
    op.drop_index("ix_mcp_grants_previous_refresh_hash", "mcp_grants")
    op.drop_column("mcp_grants", "refreshed_at")
    op.drop_column("mcp_grants", "previous_refresh_hash")
