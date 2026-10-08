from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import case, func, select, type_coerce, update
from sqlalchemy.dialects.postgresql import JSONB

from app.constants.ats import REPORT_BATCH, ConnectionStatus
from app.models.ats import AtsCandidate, AtsConnection
from app.storage.db import Session

# A finished candidate's results going back to the ATS, once (reported_at). `result` holds the
# latest results known: waiting to go back while reported_at is empty, sent once it's set. A
# corrected grade (companies' candidate.rescored) carries rescored_at, so only a newer one goes
# back again; candidate.finished's has none, the oldest.


def stamp(data: dict | None) -> str:
    """When the results' grade was stored by a rescore; empty for candidate.finished's."""
    return (data or {}).get("rescored_at") or ""


# The same, of the stored results, in SQL (JSON null and SQL NULL alike).
STORED_STAMP = func.coalesce(AtsCandidate.result["rescored_at"].astext, "")


async def offer(invite_id: UUID, data: dict) -> None:
    """A corrected grade: stored to go back (again) when it's newer than the stored results,
    sent or not; an older one or the same one delivered again changes nothing."""
    query = (
        update(AtsCandidate)
        .where(AtsCandidate.invite_id == invite_id, STORED_STAMP < stamp(data))
        .values(result=data, reported_at=None)
    )

    async with Session() as session:
        await session.execute(query)
        await session.commit()


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


async def claim(row_id: UUID) -> AtsCandidate | None:
    """Marks the results as going back before they're sent: of two events at once, only one
    gets the row, with the results stored as it was claimed, and writes to the ATS. keep() frees
    it again when they can't go now."""
    query = (
        update(AtsCandidate)
        .where(AtsCandidate.id == row_id, AtsCandidate.reported_at.is_(None))
        .values(reported_at=datetime.now(UTC))
        .returning(AtsCandidate)
    )

    async with Session() as session:
        claimed = await session.scalar(query)
        await session.commit()

    return claimed


async def keep(row_id: UUID, data: dict) -> None:
    """Results that can't go back now (a broken connection, a failing ATS): kept, to send, and
    the claim on them freed; newer ones stored meanwhile stay."""
    result = case((STORED_STAMP > stamp(data), AtsCandidate.result), else_=type_coerce(data, JSONB))
    values = {"result": result, "kept_at": datetime.now(UTC), "reported_at": None}
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


async def mark_reported(row_id: UUID, sent: dict | None) -> None:
    """These results went back, or have nowhere to go (the candidate is gone from the ATS). A
    newer grade stored meanwhile stays waiting: its own event sends it. The results stay, so a
    corrected grade delivered again is known."""
    query = (
        update(AtsCandidate)
        .where(AtsCandidate.id == row_id, STORED_STAMP == stamp(sent))
        .values(reported_at=datetime.now(UTC))
    )

    async with Session() as session:
        await session.execute(query)
        await session.commit()
