"""questions.pool: each template question's fixed pool, practice or company, replacing the
bank's stages. Revealed questions were shown with their answers, so they're practice; private
and retiring ones were used by companies but never shown, so they stay company-only. `stage`
stays, unused, for a rollback's older code, and is dropped in a later release.

Revision ID: 0027
Revises: 0026
Create Date: 2026-10-16
"""

import sqlalchemy as sa
from alembic import op

revision = "0027"
down_revision = "0026"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("questions", sa.Column("pool", sa.String(16), nullable=True))
    op.execute(
        """
        UPDATE questions SET pool = CASE WHEN stage = 'revealed' THEN 'practice' ELSE 'company' END
        WHERE topic_id IN (
            SELECT t.id FROM topics t JOIN sets s ON s.id = t.set_id WHERE s.kind = 'template'
        )
        """
    )


def downgrade() -> None:
    op.drop_column("questions", "pool")
