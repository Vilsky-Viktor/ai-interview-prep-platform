import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ShareInvite(Base):
    """Private access to a preparation for one email."""

    __tablename__ = "share_invites"
    __table_args__ = (UniqueConstraint("set_id", "email"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    set_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sets.id", ondelete="CASCADE"))
    email: Mapped[str] = mapped_column(String(320))
    token: Mapped[str] = mapped_column(String(64), unique=True)
    invited_by: Mapped[str] = mapped_column(String(128))
    accepted_by: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    # The email bounced or was marked as spam; cleared when it's sent again.
    undelivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class JoinedPreparation(Base):
    __tablename__ = "joined_preparations"

    set_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sets.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[str] = mapped_column(String(128), primary_key=True, index=True)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
