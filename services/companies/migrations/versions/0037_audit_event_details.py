"""audit_events details: what changed, such as a grade's {"from", "to"} when an answer key fix
rescored a finished candidate

Revision ID: 0037
Revises: 0036
Create Date: 2026-10-11
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0037"
down_revision = "0036"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("audit_events", sa.Column("details", JSONB))


def downgrade() -> None:
    op.drop_column("audit_events", "details")
