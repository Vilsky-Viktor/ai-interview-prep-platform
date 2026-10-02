"""drop the written reference answers from round and session snapshots

Revision ID: 0007
Revises: 0006
Create Date: 2026-10-01
"""

from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in ("rounds", "sessions"):
        op.execute(
            f"""
            UPDATE {table}
            SET questions = (
                SELECT coalesce(jsonb_agg(asked - 'reference_answer' ORDER BY position), '[]')
                FROM jsonb_array_elements(questions) WITH ORDINALITY AS item(asked, position)
            )
            """
        )


def downgrade() -> None:
    """The removed text doesn't come back."""
