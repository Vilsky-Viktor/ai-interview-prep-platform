import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


def now() -> datetime:
    return datetime.now(UTC)


class LimitSetting(Base):
    """A limit a superadmin changed from its default (prepza_common.limit_list); only changed
    ones have a row. Redis's limits:values hash, which the services read, is written from these."""

    __tablename__ = "limit_settings"

    name: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class LimitChange(Base):
    """One change of a limit: who, from what to what (None: its default), and when. Kept 24
    months."""

    __tablename__ = "limit_changes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(64))
    old_value: Mapped[float | None] = mapped_column(Float)
    new_value: Mapped[float | None] = mapped_column(Float)
    # The superadmin's account id and address (prepza's own team).
    changed_by: Mapped[str] = mapped_column(String(128))
    changed_by_email: Mapped[str] = mapped_column(String(320))
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)
