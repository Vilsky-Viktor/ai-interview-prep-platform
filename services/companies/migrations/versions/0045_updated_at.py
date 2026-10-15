"""interviews and candidate_invites updated_at: when a row last changed, set by a trigger on
every update, so the public API's lists can be synced (updated_since)

Revision ID: 0045
Revises: 0044
Create Date: 2026-10-15
"""

import sqlalchemy as sa
from alembic import op

revision = "0045"
down_revision = "0044"
branch_labels = None
depends_on = None

TABLES = ("interviews", "candidate_invites")


def upgrade() -> None:
    for table in TABLES:
        op.add_column(
            table,
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
        )

    # Rows made before: their latest known change.
    op.execute("UPDATE interviews SET updated_at = created_at")
    op.execute(
        "UPDATE candidate_invites SET updated_at = GREATEST(created_at, sent_at, "
        "COALESCE(started_at, created_at), COALESCE(finished_at, created_at))"
    )
    op.execute(
        """
        CREATE FUNCTION set_updated_at() RETURNS trigger AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
        """
    )

    for table in TABLES:
        op.execute(
            f"CREATE TRIGGER {table}_updated_at BEFORE UPDATE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION set_updated_at()"
        )

    op.create_index(
        "ix_interviews_company_updated", "interviews", ["company_id", "updated_at", "id"]
    )
    op.create_index(
        "ix_candidate_invites_interview_updated",
        "candidate_invites",
        ["interview_id", "updated_at", "id"],
    )


def downgrade() -> None:
    op.drop_index("ix_candidate_invites_interview_updated", "candidate_invites")
    op.drop_index("ix_interviews_company_updated", "interviews")

    for table in TABLES:
        op.execute(f"DROP TRIGGER {table}_updated_at ON {table}")
        op.drop_column(table, "updated_at")

    op.execute("DROP FUNCTION set_updated_at()")
