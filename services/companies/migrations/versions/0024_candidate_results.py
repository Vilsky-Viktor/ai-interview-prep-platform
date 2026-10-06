"""candidates' grade and integrity flag stored on their invite when they finish, so the list
sorts, filters and pages in SQL; indexes for lookups by generation and by candidate

Revision ID: 0024
Revises: 0023
Create Date: 2026-10-06
"""

import sqlalchemy as sa
from alembic import op

revision = "0024"
down_revision = "0023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("candidate_invites", sa.Column("grade", sa.Integer()))
    op.add_column(
        "candidate_invites",
        sa.Column("flagged", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_candidate_invites_user_id", "candidate_invites", ["user_id"])
    op.create_index("ix_interviews_generation_id", "interviews", ["generation_id"])


def downgrade() -> None:
    op.drop_index("ix_interviews_generation_id", "interviews")
    op.drop_index("ix_candidate_invites_user_id", "candidate_invites")
    op.drop_column("candidate_invites", "flagged")
    op.drop_column("candidate_invites", "grade")
