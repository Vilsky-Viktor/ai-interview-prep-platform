import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants.roles import Role
from app.models.base import Base


class Company(Base):
    __tablename__ = "companies"
    # Names are unique across prepza, ignoring case (migration 0012).
    __table_args__ = (Index("uq_companies_lower_name", text("lower(name)"), unique=True),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    members: Mapped[list["Member"]] = relationship(cascade="all, delete-orphan")


class Member(Base):
    """A company owner or admin. Invited admins bind to a user_id when they accept."""

    __tablename__ = "members"
    __table_args__ = (UniqueConstraint("company_id", "invited_email"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"))
    user_id: Mapped[str | None] = mapped_column(String(128), index=True)
    invited_email: Mapped[str] = mapped_column(String(320))
    token: Mapped[str | None] = mapped_column(String(64), unique=True)
    role: Mapped[str] = mapped_column(String(32), default=Role.ADMIN)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
