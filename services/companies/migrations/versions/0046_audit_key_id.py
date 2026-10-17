"""audit_events key_id: the API key an AI agent signed in with at the MCP server, so the action
log can tell a key from an AI app a member connected

Revision ID: 0046
Revises: 0045
Create Date: 2026-10-16
"""

import sqlalchemy as sa
from alembic import op

revision = "0046"
down_revision = "0045"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("audit_events", sa.Column("key_id", sa.Uuid(), nullable=True))


def downgrade() -> None:
    op.drop_column("audit_events", "key_id")
