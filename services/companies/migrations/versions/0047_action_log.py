"""audit_events becomes the company's action log: each action's group (the log's action filter),
what it was about (target_kind, and target_label for what isn't a person), and the event another
service sent it in (event_id, unique, so a redelivery stores it once); indexes for the member and
action filters. The nine decisions already recorded get their group and target kind. The group
stays nullable, so code rolled back to before it still records. A member's views of a
candidate's results become one row a day (UTC), the latest view's: `day` (set only for those)
under a partial unique index, the older views of a day removed.

Revision ID: 0047
Revises: 0046
Create Date: 2026-10-16
"""

import sqlalchemy as sa
from alembic import op

revision = "0047"
down_revision = "0046"
branch_labels = None
depends_on = None

GROUPS = {
    "topics_approved": "interviews",
    "pass_mark_changed": "interviews",
    "results_viewed": "candidates",
    "report_emailed": "candidates",
    "candidate_deleted": "candidates",
    "invite_revoked": "candidates",
    "extra_time_set": "candidates",
    "ownership_transferred": "team",
    "ai_apps_changed": "company",
}
KINDS = {
    "topics_approved": "interview",
    "pass_mark_changed": "interview",
    "results_viewed": "candidate",
    "candidate_deleted": "candidate",
    "invite_revoked": "candidate",
    "extra_time_set": "candidate",
    "ownership_transferred": "member",
    "ai_apps_changed": "company",
}


def upgrade() -> None:
    op.add_column("audit_events", sa.Column("group", sa.String(32), nullable=True))
    op.add_column("audit_events", sa.Column("target_kind", sa.String(32), nullable=True))
    op.add_column("audit_events", sa.Column("target_label", sa.String(256), nullable=True))
    op.add_column("audit_events", sa.Column("event_id", sa.String(128), nullable=True, unique=True))

    for action, group in GROUPS.items():
        op.execute(
            sa.text('UPDATE audit_events SET "group" = :group WHERE action = :action').bindparams(
                group=group, action=action
            )
        )

    for action, kind in KINDS.items():
        op.execute(
            sa.text(
                "UPDATE audit_events SET target_kind = :kind WHERE action = :action"
            ).bindparams(kind=kind, action=action)
        )

    # A report is emailed for a candidate or for a whole interview.
    op.execute(
        "UPDATE audit_events SET target_kind = CASE WHEN target_id IN (SELECT id FROM interviews) "
        "THEN 'interview' ELSE 'candidate' END WHERE action = 'report_emailed'"
    )
    op.add_column("audit_events", sa.Column("day", sa.Date(), nullable=True))
    op.execute(
        "DELETE FROM audit_events a USING audit_events b "
        "WHERE a.action = 'results_viewed' AND b.action = 'results_viewed' "
        "AND a.company_id = b.company_id AND a.user_id = b.user_id "
        "AND a.target_id = b.target_id "
        "AND (a.created_at AT TIME ZONE 'UTC')::date = (b.created_at AT TIME ZONE 'UTC')::date "
        "AND (a.created_at, a.id) < (b.created_at, b.id)"
    )
    op.execute(
        "UPDATE audit_events SET day = (created_at AT TIME ZONE 'UTC')::date "
        "WHERE action = 'results_viewed'"
    )
    op.create_index(
        "uq_audit_events_results_viewed_day",
        "audit_events",
        ["company_id", "user_id", "target_id", "day"],
        unique=True,
        postgresql_where=sa.text("action = 'results_viewed'"),
    )
    op.create_index(
        "ix_audit_events_company_id_user_id_created_at",
        "audit_events",
        ["company_id", "user_id", "created_at"],
    )
    op.create_index(
        "ix_audit_events_company_id_group_created_at",
        "audit_events",
        ["company_id", "group", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("uq_audit_events_results_viewed_day", "audit_events")
    op.drop_column("audit_events", "day")
    op.drop_index("ix_audit_events_company_id_group_created_at", "audit_events")
    op.drop_index("ix_audit_events_company_id_user_id_created_at", "audit_events")
    op.drop_column("audit_events", "event_id")
    op.drop_column("audit_events", "target_label")
    op.drop_column("audit_events", "target_kind")
    op.drop_column("audit_events", "group")
