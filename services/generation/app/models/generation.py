import uuid
from datetime import datetime

from prepza_common.constants import DEFAULT_LANGUAGE
from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.constants.statuses import Status
from app.models.base import Base


class Generation(Base):
    __tablename__ = "generations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_uid: Mapped[str] = mapped_column(String(128), index=True)
    kind: Mapped[str] = mapped_column(String(32), default="preparation")
    company_id: Mapped[uuid.UUID | None]
    text: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(8), default=DEFAULT_LANGUAGE)
    status: Mapped[str] = mapped_column(String(32), default=Status.QUEUED)
    # A learner's first kit: free, with fewer topics (FREE_KIT_TOPICS).
    free_kit: Mapped[bool] = mapped_column(Boolean, default=False)
    topics: Mapped[list | None] = mapped_column(JSONB)
    progress: Mapped[dict | None] = mapped_column(JSONB)
    preparation_id: Mapped[uuid.UUID | None]
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
