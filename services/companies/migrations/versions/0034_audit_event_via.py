"""audit_events via: what an event was recorded through when not a person in the app (the in-app
assistant); None for every event so far

Revision ID: 0034
Revises: 0033
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op

revision = "0034"
down_revision = "0033"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("audit_events", sa.Column("via", sa.String(32), nullable=True))


def downgrade() -> None:
    op.drop_column("audit_events", "via")
