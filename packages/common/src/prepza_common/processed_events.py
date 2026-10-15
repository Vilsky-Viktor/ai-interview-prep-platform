# Handling a Pub/Sub event once: its id is noted in the same transaction as what it changes, so a
# redelivery finds it and changes nothing. `model` is the service's ProcessedEventColumns table.
from datetime import datetime

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession


async def claim(session: AsyncSession, model, event_id: str | None) -> bool:
    """Notes the event in `session`; False when it was handled before. A second delivery
    running at the same time waits here until the first commits or rolls back. Without an id
    (not from an event), always True."""
    if event_id is None:
        return True

    inserted = await session.scalar(
        insert(model).values(event_id=event_id).on_conflict_do_nothing().returning(model.event_id)
    )

    return inserted is not None


async def forget(sessionmaker, model, before: datetime) -> int:
    """Drops the notes of events received before `before`, long past Pub/Sub's redeliveries."""
    async with sessionmaker() as session:
        result = await session.execute(delete(model).where(model.received_at < before))
        await session.commit()

        return result.rowcount
