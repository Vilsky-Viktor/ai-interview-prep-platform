"""entries.note: why a superadmin adjusted a company's credits, as its history shows it

Revision ID: 0014
Revises: 0013
Create Date: 2026-10-16
"""

import sqlalchemy as sa
from alembic import op

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("entries", sa.Column("note", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("entries", "note")
