import uuid

from sqlalchemy import func, select, update

from app.constants.integrity import MAX_SIGNALS_PER_QUESTION, IntegritySignal
from app.models.signals import Signal
from app.storage.db import Session as Db


async def set_away(session_id: uuid.UUID, seconds: float) -> None:
    """How long the session's latest page leave lasted, once the candidate is back; a return
    without a leave changes nothing."""
    latest = (
        select(Signal.id)
        .where(
            Signal.session_id == session_id,
            Signal.kind == IntegritySignal.TAB_LEAVE,
            Signal.away_seconds.is_(None),
        )
        .order_by(Signal.created_at.desc())
        .limit(1)
        .scalar_subquery()
    )

    async with Db() as session:
        await session.execute(
            update(Signal).where(Signal.id == latest).values(away_seconds=seconds)
        )
        await session.commit()


async def add_signal(
    session_id: uuid.UUID, question_id: uuid.UUID | None, kind: IntegritySignal
) -> None:
    """Saves the signal, unless its question already holds MAX_SIGNALS_PER_QUESTION."""
    kept = select(func.count()).where(
        Signal.session_id == session_id, Signal.question_id.is_not_distinct_from(question_id)
    )

    async with Db() as session:
        if await session.scalar(kept) >= MAX_SIGNALS_PER_QUESTION:
            return

        session.add(Signal(session_id=session_id, question_id=question_id, kind=kind))
        await session.commit()
