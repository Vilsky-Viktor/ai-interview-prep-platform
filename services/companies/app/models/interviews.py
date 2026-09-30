import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    set_id: Mapped[uuid.UUID | None]
    generation_id: Mapped[uuid.UUID]
    mode: Mapped[str] = mapped_column(String(32))
    share_results: Mapped[bool]
    topic_limits: Mapped[dict[str, int]] = mapped_column(
        JSONB, default=dict, server_default="{}"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    invites: Mapped[list["CandidateInvite"]] = relationship(cascade="all, delete-orphan")
