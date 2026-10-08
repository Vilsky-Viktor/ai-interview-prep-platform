"""the superadmin who changed a user's email settings on their behalf

Revision ID: 0024
Revises: 0023
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op

revision = "0024"
down_revision = "0023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("email_consents", sa.Column("changed_by", sa.String(128), nullable=True))


def downgrade() -> None:
    op.drop_column("email_consents", "changed_by")
