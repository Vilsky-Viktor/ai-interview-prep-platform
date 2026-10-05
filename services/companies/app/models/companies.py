import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Index, LargeBinary, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants.roles import Role
from app.models.base import Base


class Company(Base):
    __tablename__ = "companies"
    # Names are unique across prepza, ignoring case (migration 0012).
    __table_args__ = (Index("uq_companies_lower_name", text("lower(name)"), unique=True),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200))
    # The company's logo on candidates' pages, emails and reports: the image itself (small,
    # loaded only when served), its media type, and a version that changes with every upload so
    # its address can be cached for good.
    logo: Mapped[bytes | None] = mapped_column(LargeBinary, deferred=True)
    logo_type: Mapped[str | None] = mapped_column(String(32))
    logo_version: Mapped[int] = mapped_column(default=0, server_default="0")
    # Verification by work email: the website's domain an owner or admin gave, and the same
    # domain once one of them signed in with a verified email on it. The badge shows it.
    website_domain: Mapped[str | None] = mapped_column(String(253))
    verified_domain: Mapped[str | None] = mapped_column(String(253))
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
