"""no learners: personal wallets, their history, holds, referrals and gifts go

Purchases stay for the accounts.

Revision ID: 0008
Revises: 0007
Create Date: 2026-10-05
"""

from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in ("wallets", "entries", "holds", "referrals", "auto_top_ups"):
        op.execute(f"DELETE FROM {table} WHERE owner_type = 'user'")

    op.execute("DELETE FROM gifts WHERE key LIKE 'user:%'")
    # Only certificates had a note.
    op.drop_column("entries", "note")


def downgrade() -> None:
    raise NotImplementedError("The learner data was deleted; it can't be brought back.")
