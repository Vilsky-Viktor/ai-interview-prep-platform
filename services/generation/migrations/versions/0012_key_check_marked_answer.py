"""key_checks: the option marked correct when the check was queued, so a result for a key moved
since is dropped

Revision ID: 0012
Revises: 0011
Create Date: 2026-10-06
"""

import sqlalchemy as sa
from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("key_checks", sa.Column("marked_answer", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("key_checks", "marked_answer")
