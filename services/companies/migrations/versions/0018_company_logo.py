"""company branding: a logo on candidates' pages, emails and reports

Revision ID: 0018
Revises: 0017
Create Date: 2026-10-05
"""

import sqlalchemy as sa
from alembic import op

revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("companies", sa.Column("logo", sa.LargeBinary(), nullable=True))
    op.add_column("companies", sa.Column("logo_type", sa.String(32), nullable=True))
    op.add_column(
        "companies",
        sa.Column("logo_version", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("companies", "logo_version")
    op.drop_column("companies", "logo_type")
    op.drop_column("companies", "logo")
