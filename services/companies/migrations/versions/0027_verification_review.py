"""verification review: a work email on the website's domain sends the company for a
superadmin's review; only an approved one keeps the badge

Revision ID: 0027
Revises: 0026
Create Date: 2026-10-06
"""

import sqlalchemy as sa
from alembic import op

revision = "0027"
down_revision = "0026"
branch_labels = None
depends_on = None

COLUMNS = (
    "verification_email",
    "verification_name",
    "verification_submitted_at",
    "decline_reason",
    "verification_decided_by",
    "verification_decided_at",
)


def upgrade() -> None:
    op.add_column(
        "companies",
        sa.Column("verification_status", sa.String(16), nullable=False, server_default="none"),
    )
    op.add_column("companies", sa.Column("verification_email", sa.String(320)))
    op.add_column("companies", sa.Column("verification_name", sa.String(200)))
    op.add_column("companies", sa.Column("verification_submitted_at", sa.DateTime(timezone=True)))
    op.add_column("companies", sa.Column("decline_reason", sa.String(500)))
    op.add_column("companies", sa.Column("verification_decided_by", sa.String(128)))
    op.add_column("companies", sa.Column("verification_decided_at", sa.DateTime(timezone=True)))
    # Companies verified before the review keep their badge; a website still waiting for a
    # work email keeps waiting.
    op.execute(
        "UPDATE companies SET verification_status = 'approved', verification_name = name "
        "WHERE verified_domain IS NOT NULL"
    )
    op.execute(
        "UPDATE companies SET verification_status = 'waiting_email' "
        "WHERE website_domain IS NOT NULL AND verified_domain IS NULL"
    )


def downgrade() -> None:
    for column in COLUMNS:
        op.drop_column("companies", column)

    op.drop_column("companies", "verification_status")
