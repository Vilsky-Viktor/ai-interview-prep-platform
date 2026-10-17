"""messages.page: the page a user's message was asked on (its key, path and ids), so "here" in
an earlier message keeps meaning where the user was then

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-16
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("messages", sa.Column("page", JSONB))


def downgrade() -> None:
    op.drop_column("messages", "page")
