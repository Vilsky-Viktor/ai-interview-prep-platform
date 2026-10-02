"""pgvector embedding per topic, for reusing questions from similar public topics

Revision ID: 0011
Revises: 0010
Create Date: 2026-10-01
"""

from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    # Not in the ORM model: only the raw SQL in storage/reuse.py reads or writes it.
    op.execute("ALTER TABLE topics ADD COLUMN embedding vector(256)")


def downgrade() -> None:
    op.execute("ALTER TABLE topics DROP COLUMN embedding")
