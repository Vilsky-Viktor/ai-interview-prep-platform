"""answer events counted once, flags re-sent to the verifier, reporters kept across revisions,
and an index for finding templates

Revision ID: 0019
Revises: 0018
Create Date: 2026-10-06
"""

import sqlalchemy as sa
from alembic import op

revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "processed_events",
        sa.Column("event_id", sa.String(128), primary_key=True),
        sa.Column(
            "received_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_processed_events_received_at", "processed_events", ["received_at"])

    op.add_column("question_stats", sa.Column("flagged_at", sa.DateTime(timezone=True)))
    # Flags saved before this are dated by the stats' last change, so the sweep re-sends the old.
    op.execute("UPDATE question_stats SET flagged_at = updated_at WHERE flag IS NOT NULL")
    op.create_index(
        "ix_question_stats_flagged_at",
        "question_stats",
        ["flagged_at"],
        postgresql_where=sa.text("flag IS NOT NULL"),
    )

    op.create_table(
        "question_reporters",
        sa.Column(
            "question_id",
            sa.Uuid(),
            sa.ForeignKey("questions.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("user_id", sa.String(128), primary_key=True),
    )
    op.create_index("ix_question_reporters_user_id", "question_reporters", ["user_id"])
    op.execute(
        "INSERT INTO question_reporters (question_id, user_id) "
        "SELECT question_id, user_id FROM question_reports ON CONFLICT DO NOTHING"
    )

    op.create_index("ix_sets_kind_level_language", "sets", ["kind", "level", "language"])


def downgrade() -> None:
    op.drop_index("ix_sets_kind_level_language", table_name="sets")
    op.drop_index("ix_question_reporters_user_id", table_name="question_reporters")
    op.drop_table("question_reporters")
    op.drop_index("ix_question_stats_flagged_at", table_name="question_stats")
    op.drop_column("question_stats", "flagged_at")
    op.drop_index("ix_processed_events_received_at", table_name="processed_events")
    op.drop_table("processed_events")
