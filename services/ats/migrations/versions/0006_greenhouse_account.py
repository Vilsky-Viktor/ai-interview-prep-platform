"""ats_connections account: Greenhouse's is blank, as it names no account (it was the
credential's last characters)

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-10
"""

from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE ats_connections SET account = '' WHERE provider = 'greenhouse'")


def downgrade() -> None:
    pass
