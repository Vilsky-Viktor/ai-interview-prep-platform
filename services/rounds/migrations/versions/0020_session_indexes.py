"""sessions: one per candidate and topic, and indexes for running sections and interview data

Revision ID: 0020
Revises: 0019
Create Date: 2026-10-05
"""

from alembic import op

revision = "0020"
down_revision = "0019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Two starts at once (a double click, two tabs) must not create a second set of sections.
    op.create_unique_constraint(
        "uq_sessions_invite_topic", "sessions", ["candidate_invite_id", "topic_id"]
    )
    # The expiry check every minute only looks at interviews with a section still running.
    op.create_index(
        "ix_sessions_running_invite",
        "sessions",
        ["candidate_invite_id"],
        postgresql_where="status = 'in_progress'",
    )
    op.create_index("ix_sessions_interview_set_id", "sessions", ["interview_set_id"])


def downgrade() -> None:
    op.drop_index("ix_sessions_interview_set_id", table_name="sessions")
    op.drop_index("ix_sessions_running_invite", table_name="sessions")
    op.drop_constraint("uq_sessions_invite_topic", "sessions", type_="unique")
