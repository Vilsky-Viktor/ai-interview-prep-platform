import uuid

from sqlalchemy import update as sql_update

from app.constants.statuses import Status
from app.models.generation import Generation
from app.storage.db import Session


async def create(
    owner_uid: str, text: str, kind: str = "preparation", company_id=None
) -> Generation:
    async with Session() as session:
        generation = Generation(
            owner_uid=owner_uid,
            kind=kind,
            company_id=company_id,
            text=text,
            status=Status.QUEUED,
        )
        session.add(generation)
        await session.commit()

        return generation


async def get(generation_id: uuid.UUID) -> Generation | None:
    async with Session() as session:
        return await session.get(Generation, generation_id)


async def update(generation_id: uuid.UUID, **values) -> None:
    async with Session() as session:
        await session.execute(
            sql_update(Generation).where(Generation.id == generation_id).values(**values)
        )
        await session.commit()


async def claim_review(generation_id: uuid.UUID) -> bool:
    """Atomically move a generation from awaiting review back to the queue."""
    async with Session() as session:
        result = await session.execute(
            sql_update(Generation)
            .where(Generation.id == generation_id, Generation.status == Status.AWAITING_REVIEW)
            .values(status=Status.QUEUED)
        )
        await session.commit()

        return result.rowcount == 1


async def claim_retry(generation_id: uuid.UUID) -> bool:
    """Atomically move a failed generation back to the queue."""
    async with Session() as session:
        result = await session.execute(
            sql_update(Generation)
            .where(Generation.id == generation_id, Generation.status == Status.FAILED)
            .values(status=Status.QUEUED, error=None)
        )
        await session.commit()

        return result.rowcount == 1
