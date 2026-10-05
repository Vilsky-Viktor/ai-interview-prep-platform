from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TalentLink(Base):
    """A talent's answer to being suggested to companies, asked once before their first practice:
    their LinkedIn link and the name from their sign-in, or no link when they
    declined or withdrew. `decided_at` is when they last answered."""

    __tablename__ = "talent_links"

    user_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(Text)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
