from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update

from app.constants.ats import REPORT_BATCH, ConnectionStatus
from app.models.ats import AtsCandidate, AtsConnection
from app.storage.db import Session

# A finished candidate's results going back to the ATS, once (reported_at).


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


async def claim(row_id: UUID) -> bool:
    """Marks the results as going back before they're sent: of two events at once, only one
    gets True and writes to the ATS. keep() frees it again when they can't go now."""
    query = (
        update(AtsCandidate)
        .where(AtsCandidate.id == row_id, AtsCandidate.reported_at.is_(None))
        .values(reported_at=datetime.now(UTC))
        .returning(AtsCandidate.id)
    )

    async with Session() as session:
        claimed = await session.scalar(query)
        await session.commit()

    return claimed is not None


async def keep(row_id: UUID, data: dict) -> None:
    """Results that can't go back now (a broken connection, a failing ATS): kept, to send, and
    the claim on them freed."""
    values = {"result": data, "kept_at": datetime.now(UTC), "reported_at": None}
    query = update(AtsCandidate).where(AtsCandidate.id == row_id).values(**values)

    async with Session() as session:
        await session.execute(query)
        await session.commit()


async def unreported() -> list[AtsCandidate]:
    """Kept results of working connections, longest kept first, as many as one run sends."""
    working = select(AtsConnection.id).where(AtsConnection.status == ConnectionStatus.CONNECTED)
    query = (
        select(AtsCandidate)
        .where(
            AtsCandidate.connection_id.in_(working),
            AtsCandidate.result.is_not(None),
            AtsCandidate.reported_at.is_(None),
        )
        .order_by(AtsCandidate.kept_at)
        .limit(REPORT_BATCH)
    )

    async with Session() as session:
        return list((await session.scalars(query)).all())


async def mark_reported(row_id: UUID) -> None:
    """Their results went back, or have nowhere to go (the candidate is gone from the ATS)."""
    query = (
        update(AtsCandidate)
        .where(AtsCandidate.id == row_id)
        .values(reported_at=datetime.now(UTC), result=None)
    )

    async with Session() as session:
        await session.execute(query)
        await session.commit()
