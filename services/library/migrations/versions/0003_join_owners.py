"""join preparation owners

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-29
"""

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO joined_preparations (set_id, user_id, joined_at)
        SELECT id, owner_id, created_at
        FROM sets
        WHERE kind = 'preparation' AND owner_type = 'user'
        ON CONFLICT DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM joined_preparations AS joined
        USING sets
        WHERE joined.set_id = sets.id
          AND joined.user_id = sets.owner_id
          AND sets.kind = 'preparation'
          AND sets.owner_type = 'user'
        """
    )
