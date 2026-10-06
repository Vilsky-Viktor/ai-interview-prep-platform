from datetime import datetime

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.events import ProcessedEvent
from app.storage.db import Session


async def claim(session: AsyncSession, event_id: str) -> bool:
    """Notes the event in `session`; False when it was processed before. A second delivery
    running at the same time waits here until the first commits or rolls back."""
    inserted = await session.scalar(
        insert(ProcessedEvent)
        .values(event_id=event_id)
        .on_conflict_do_nothing()
        .returning(ProcessedEvent.event_id)
    )

    return inserted is not None


async def forget(before: datetime) -> int:
    """Drops the notes of events received before `before`, long past Pub/Sub's redeliveries."""
    async with Session() as session:
        result = await session.execute(
            delete(ProcessedEvent).where(ProcessedEvent.received_at < before)
        )
        await session.commit()

        return result.rowcount
