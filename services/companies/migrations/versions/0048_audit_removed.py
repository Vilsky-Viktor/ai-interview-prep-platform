"""audit_events removed: what an action took away (an API key's narrowed permissions), so the
action log shows it

Revision ID: 0048
Revises: 0047
Create Date: 2026-10-17
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0048"
down_revision = "0047"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "audit_events", sa.Column("removed", postgresql.ARRAY(sa.String(64)), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("audit_events", "removed")
