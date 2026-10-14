"""terms_acceptances: the terms' version each new account accepted when signing up

Revision ID: 0026
Revises: 0025
Create Date: 2026-10-14
"""

import sqlalchemy as sa
from alembic import op

revision = "0026"
down_revision = "0025"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "terms_acceptances",
        sa.Column("user_id", sa.String(128), primary_key=True),
        sa.Column("version", sa.String(10), primary_key=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("terms_acceptances")
