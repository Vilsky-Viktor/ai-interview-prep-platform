"""audit_events details dropped: nothing records what changed any more, since an answer key fix
applies only to candidates who start after it

Revision ID: 0038
Revises: 0037
Create Date: 2026-10-11
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0038"
down_revision = "0037"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("audit_events", "details")


def downgrade() -> None:
    op.add_column("audit_events", sa.Column("details", JSONB))
