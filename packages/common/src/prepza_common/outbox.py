import logging
from datetime import UTC, datetime, timedelta

from prepza_common import pubsub
from prepza_common.constants import OUTBOX_BATCH, OUTBOX_KEEP_DAYS
from sqlalchemy import delete, select

logger = logging.getLogger(__name__)


def add(session, model, event_type: str, data: dict) -> None:
    """Saves an event in the caller's transaction, so it exists exactly when the change does."""
    session.add(model(event_type=event_type, data=data))


async def flush(sessionmaker, model) -> int:
    """Publishes waiting events, oldest first, and returns how many. Two runs never send the same
    row (SKIP LOCKED); a failure keeps the rest for the next run. Published rows go after
    OUTBOX_KEEP_DAYS."""
    published = 0

    async with sessionmaker() as session:
        waiting = await session.scalars(
            select(model)
            .where(model.published_at.is_(None))
            .order_by(model.created_at)
            .limit(OUTBOX_BATCH)
            .with_for_update(skip_locked=True)
        )

        try:
            for row in waiting:
                await pubsub.publish(row.event_type, row.data)
                row.published_at = datetime.now(UTC)
                published += 1
        finally:
            await session.execute(
                delete(model).where(
                    model.published_at < datetime.now(UTC) - timedelta(days=OUTBOX_KEEP_DAYS)
                )
            )
            await session.commit()

    return published


async def flush_quietly(sessionmaker, model) -> None:
    """Right after a change: publishes at once when it can. A failure is only logged, as the
    scheduled flush sends the event a minute later."""
    try:
        await flush(sessionmaker, model)
    except Exception:
        logger.exception("Couldn't publish waiting events; the scheduled flush will")
