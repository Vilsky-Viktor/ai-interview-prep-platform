"""api: api_keys.permissions, what each key may do. Keys made before keep every API permission,
so they work as they did; using them with AI agents (MCP) stays off, so their reach never grows.

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-16
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

# Every permission but "mcp", as constants/permissions.py names them today.
EXISTING = [
    "interviews:read",
    "interviews:create",
    "candidates:read",
    "candidates:invite",
    "candidates:change",
    "candidates:delete",
    "credits:read",
]
# A key made by code that doesn't name its permissions (an older version, rolled back to) gets
# a new key's defaults.
DEFAULT = ["interviews:read", "candidates:read"]


def array(items: list[str]) -> sa.TextClause:
    return sa.text("ARRAY[" + ", ".join(f"'{item}'" for item in items) + "]::varchar(32)[]")


def upgrade() -> None:
    op.add_column(
        "api_keys",
        sa.Column(
            "permissions", ARRAY(sa.String(32)), nullable=False, server_default=array(EXISTING)
        ),
    )
    op.alter_column("api_keys", "permissions", server_default=array(DEFAULT))


def downgrade() -> None:
    op.drop_column("api_keys", "permissions")
