from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SlackConnection(Base):
    """A company's Slack channel: its notifications of the kinds it chose are posted there."""

    __tablename__ = "slack_connections"

    company_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    # The workspace and channel, as Slack names them, to show.
    team: Mapped[str] = mapped_column(String(200))
    channel: Mapped[str] = mapped_column(String(200))
    # The channel's web hook and the app's token (to revoke it), sealed with SLACK_ENCRYPTION_KEY.
    webhook: Mapped[str] = mapped_column(Text)
    token: Mapped[str] = mapped_column(Text)
    kinds: Mapped[list] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(16))
    created_by: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
