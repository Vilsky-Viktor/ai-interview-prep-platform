import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.constants.invites import InviteStatus
from app.models.base import Base


class CandidateInvite(Base):
    __tablename__ = "candidate_invites"
    __table_args__ = (UniqueConstraint("interview_id", "email"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    interview_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("interviews.id", ondelete="CASCADE"), index=True
    )
    email: Mapped[str] = mapped_column(String(320))
    token: Mapped[str] = mapped_column(String(64), unique=True)
    user_id: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), default=InviteStatus.INVITED)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    # When the invite email was last sent; an invite never started expires INVITE_EXPIRY_DAYS
    # after it.
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    # When the one reminder went out; sending the invite again clears it.
    reminded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Extra time for a candidate who needs it (an accommodation), in percent of each question's
    # time; set before they start.
    extra_time: Mapped[int] = mapped_column(default=0, server_default="0")
