import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class HiddenTalent(Base):
    """A suggested talent a company hid from a test's list, by their LinkedIn link."""

    __tablename__ = "hidden_talents"

    interview_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("interviews.id", ondelete="CASCADE"), primary_key=True
    )
    url: Mapped[str] = mapped_column(String(300), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
