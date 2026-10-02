"""flagged questions waiting for a key check in an OpenAI batch

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-01
"""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "key_checks",
        sa.Column("question_id", sa.Uuid(), primary_key=True),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("batch_id", sa.String(64), nullable=True, index=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )


def downgrade() -> None:
    op.drop_table("key_checks")
