import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.constants.ats import ConnectionStatus
from app.models.base import Base


class AtsConnection(Base):
    """A company's connection to its applicant tracking system: one per company and ATS."""

    __tablename__ = "ats_connections"
    __table_args__ = (UniqueConstraint("company_id", "provider"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    provider: Mapped[str] = mapped_column(String(32))
    # What the company sees it connected as (Workable's subdomain).
    account: Mapped[str] = mapped_column(String(200))
    # The ATS key, encrypted (helpers/encryption.py); never returned to the browser.
    credentials: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default=ConnectionStatus.CONNECTED)
    # Who connected it: their invites and limits apply to candidates the ATS sends.
    created_by: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class AtsJobLink(Base):
    """An ATS job linked to a prepza interview: candidates who reach `stage_id` in that job get
    the interview."""

    __tablename__ = "ats_job_links"
    __table_args__ = (UniqueConstraint("connection_id", "job_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    connection_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ats_connections.id", ondelete="CASCADE"), index=True
    )
    interview_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("interviews.id", ondelete="CASCADE"), index=True
    )
    # The ATS's own ids, and their names as they were when linked.
    job_id: Mapped[str] = mapped_column(String(100))
    job_name: Mapped[str] = mapped_column(String(300))
    stage_id: Mapped[str] = mapped_column(String(100))
    stage_name: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
