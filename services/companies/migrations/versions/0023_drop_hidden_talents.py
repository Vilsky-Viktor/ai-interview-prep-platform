"""drop hidden talents: talent suggestions are removed

Revision ID: 0023
Revises: 0022
Create Date: 2026-10-06
"""

import sqlalchemy as sa
from alembic import op

revision = "0023"
down_revision = "0022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("hidden_talents")


def downgrade() -> None:
    op.create_table(
        "hidden_talents",
        sa.Column(
            "interview_id",
            sa.Uuid(),
            sa.ForeignKey("interviews.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("url", sa.String(300), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
