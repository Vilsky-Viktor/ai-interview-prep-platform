from datetime import UTC, datetime, timedelta
from uuid import UUID

from prepza_common import outbox
from prepza_common.notifications import NOTIFICATION_REQUESTED
from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.dialects.postgresql import insert

from app.constants.ats import STALE_CLAIM_MINUTES, CandidateStatus
from app.models.ats import AtsCandidate, AtsConnection
from app.models.outbox import OutboxEvent
from app.storage.db import Session


async def add(
    connection_id: UUID, link_id: UUID, interview_id: UUID, candidate_id: str, email: str
) -> AtsCandidate:
    """The ATS's candidate for the interview: saved waiting the first time, the same row when
    the event comes again (or twice at once: the unique key keeps one)."""
    query = (
        insert(AtsCandidate)
        .values(
            connection_id=connection_id,
            link_id=link_id,
            interview_id=interview_id,
            candidate_id=candidate_id,
            email=email.lower(),
            status=CandidateStatus.WAITING,
        )
        .on_conflict_do_nothing(index_elements=["connection_id", "candidate_id", "interview_id"])
    )
    existing = select(AtsCandidate).where(
        AtsCandidate.connection_id == connection_id,
        AtsCandidate.candidate_id == candidate_id,
        AtsCandidate.interview_id == interview_id,
    )

    async with Session() as session:
        await session.execute(query)
        await session.commit()

        return await session.scalar(existing)


def _stale():
    """An invite started this long ago and never settled: the server stopped mid-invite."""
    return and_(
        AtsCandidate.status == CandidateStatus.INVITING,
        AtsCandidate.claimed_at < datetime.now(UTC) - timedelta(minutes=STALE_CLAIM_MINUTES),
    )


async def claim(row_id: UUID, statuses: tuple[str, ...]) -> bool:
    """Marks a candidate as being invited, if it's in one of `statuses` or its last invite was
    cut off: of two requests at once, only one gets True and invites."""
    query = (
        update(AtsCandidate)
        .where(AtsCandidate.id == row_id, or_(AtsCandidate.status.in_(statuses), _stale()))
        .values(status=CandidateStatus.INVITING, claimed_at=datetime.now(UTC))
        .returning(AtsCandidate.id)
    )

    async with Session() as session:
        claimed = await session.scalar(query)
        await session.commit()

    return claimed is not None


async def stale(company_id: UUID | None = None) -> list[AtsCandidate]:
    """Invites cut off midway, of one company or all, to start again."""
    query = select(AtsCandidate).where(_stale())

    if company_id is not None:
        owned = select(AtsConnection.id).where(AtsConnection.company_id == company_id)
        query = query.where(AtsCandidate.connection_id.in_(owned))

    async with Session() as session:
        return list((await session.scalars(query)).all())


async def settle(
    row_id: UUID,
    status: str,
    reason: str | None = None,
    invite_id: UUID | None = None,
    notice: dict | None = None,
) -> None:
    """The candidate's outcome, with the company's notification about it in the same
    transaction (the outbox sends it)."""
    query = (
        update(AtsCandidate)
        .where(AtsCandidate.id == row_id)
        .values(status=status, reason=reason, invite_id=invite_id)
    )

    async with Session() as session:
        await session.execute(query)

        if notice:
            outbox.add(session, OutboxEvent, NOTIFICATION_REQUESTED, notice)

        await session.commit()


async def with_status(status: str, *, interview_id=None, company_id=None) -> list[AtsCandidate]:
    """The candidates in `status`, of one interview or of one company's connections."""
    query = select(AtsCandidate).where(AtsCandidate.status == status)

    if interview_id is not None:
        query = query.where(AtsCandidate.interview_id == interview_id)

    if company_id is not None:
        owned = select(AtsConnection.id).where(AtsConnection.company_id == company_id)
        query = query.where(AtsCandidate.connection_id.in_(owned))

    async with Session() as session:
        return list((await session.scalars(query)).all())


async def for_invite(invite_id: UUID) -> tuple[AtsCandidate, AtsConnection] | None:
    """The ATS candidate an invite came from, with its connection, until its results went back."""
    query = (
        select(AtsCandidate, AtsConnection)
        .join(AtsConnection, AtsConnection.id == AtsCandidate.connection_id)
        .where(AtsCandidate.invite_id == invite_id, AtsCandidate.reported_at.is_(None))
    )

    async with Session() as session:
        row = (await session.execute(query)).first()

        return tuple(row) if row else None


async def mark_reported(row_id: UUID) -> None:
    query = (
        update(AtsCandidate).where(AtsCandidate.id == row_id).values(reported_at=datetime.now(UTC))
    )

    async with Session() as session:
        await session.execute(query)
        await session.commit()


async def counts(company_id: UUID) -> dict[UUID, dict[str, int]]:
    """Per linked job of the company: how many candidates are in each status."""
    owned = select(AtsConnection.id).where(AtsConnection.company_id == company_id)
    query = (
        select(AtsCandidate.link_id, AtsCandidate.status, func.count())
        .where(AtsCandidate.connection_id.in_(owned), AtsCandidate.link_id.is_not(None))
        .group_by(AtsCandidate.link_id, AtsCandidate.status)
    )
    found: dict[UUID, dict[str, int]] = {}

    async with Session() as session:
        for link_id, status, count in (await session.execute(query)).all():
            found.setdefault(link_id, {})[status] = count

    return found
