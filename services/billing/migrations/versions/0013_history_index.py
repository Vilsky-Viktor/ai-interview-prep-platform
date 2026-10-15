"""entries ix_entries_history: a wallet's history page reads its newest entries from an index
instead of sorting all of them

Revision ID: 0013
Revises: 0012
Create Date: 2026-10-15
"""

from alembic import op

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX ix_entries_history ON entries (owner_type, owner_id, created_at DESC, id)"
    )


def downgrade() -> None:
    op.drop_index("ix_entries_history", "entries")
