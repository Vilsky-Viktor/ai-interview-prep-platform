import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Text, false
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants.interviews import DEFAULT_TIME_LIMIT_MINUTES
from app.models.base import Base


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    set_id: Mapped[uuid.UUID | None]
    # Copied from the generated set (and renames), so pages don't ask library for it.
    title: Mapped[str | None] = mapped_column(Text)
    generation_id: Mapped[uuid.UUID]
    share_results: Mapped[bool]
    # A timed interview finishes by itself time_limit_minutes after the candidate starts.
    timed: Mapped[bool] = mapped_column(default=False, server_default=false())
    time_limit_minutes: Mapped[int] = mapped_column(
        default=DEFAULT_TIME_LIMIT_MINUTES, server_default=str(DEFAULT_TIME_LIMIT_MINUTES)
    )
    topic_limits: Mapped[dict[str, int]] = mapped_column(
        JSONB, default=dict, server_default="{}"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    invites: Mapped[list["CandidateInvite"]] = relationship(cascade="all, delete-orphan")
