"""hidden talents: suggested talents a company hid from a test's list

Revision ID: 0020
Revises: 0019
Create Date: 2026-10-05
"""

import sqlalchemy as sa
from alembic import op

revision = "0020"
down_revision = "0019"
branch_labels = None
depends_on = None


def upgrade() -> None:
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


def downgrade() -> None:
    op.drop_table("hidden_talents")
