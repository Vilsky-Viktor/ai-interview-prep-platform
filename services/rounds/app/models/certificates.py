import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Certificate(Base):
    __tablename__ = "certificates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    user_name: Mapped[str] = mapped_column(Text)
    round_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("rounds.id", ondelete="CASCADE"), unique=True
    )
    topic_id: Mapped[uuid.UUID]
    topic_title: Mapped[str] = mapped_column(Text)
    score: Mapped[int]
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now()
    )
