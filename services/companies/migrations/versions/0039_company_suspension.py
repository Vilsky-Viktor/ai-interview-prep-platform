"""companies suspended_at: a superadmin suspends a company (impersonation, abuse), and nothing
new happens for it until it's lifted

Revision ID: 0039
Revises: 0038
Create Date: 2026-10-14
"""

import sqlalchemy as sa
from alembic import op

revision = "0039"
down_revision = "0038"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("companies", sa.Column("suspended_at", sa.DateTime(timezone=True)))


def downgrade() -> None:
    op.drop_column("companies", "suspended_at")
