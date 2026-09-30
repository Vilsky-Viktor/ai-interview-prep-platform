"""member invite tokens

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-29
"""

import secrets

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("members", sa.Column("token", sa.String(64), unique=True))
    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id FROM members WHERE user_id IS NULL")).fetchall()

    for row in rows:
        conn.execute(
            sa.text("UPDATE members SET token = :token WHERE id = :id"),
            {"token": secrets.token_urlsafe(32), "id": row.id},
        )


def downgrade() -> None:
    op.drop_column("members", "token")
