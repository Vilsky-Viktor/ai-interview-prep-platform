"""legal_notices: the legal documents' versions whose change a superadmin asked to email

Revision ID: 0007
Revises: 0006
Create Date: 2026-10-14
"""

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "legal_notices",
        sa.Column("document", sa.String(16), primary_key=True),
        sa.Column("version", sa.String(10), primary_key=True),
        sa.Column("asked_by", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table("legal_notices")
