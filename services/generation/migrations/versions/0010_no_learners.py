"""no learners: prep kit generations and the approved flag go

Revision ID: 0010
Revises: 0009
Create Date: 2026-10-05
"""

from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DELETE FROM generations WHERE kind <> 'interview'")
    op.drop_column("generations", "approved")


def downgrade() -> None:
    raise NotImplementedError("The learner data was deleted; it can't be brought back.")
