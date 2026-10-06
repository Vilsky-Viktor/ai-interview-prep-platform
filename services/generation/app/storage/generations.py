import uuid
from datetime import datetime

from prepza_common import outbox
from prepza_common.constants import DEFAULT_LANGUAGE
from sqlalchemy import String, and_, bindparam, or_, select, text
from sqlalchemy import update as sql_update

from app.constants.events import GENERATION_CANCELLED
from app.constants.kinds import GenerationKind
from app.constants.statuses import FINISHED, Status
from app.models.generation import Generation
from app.models.outbox import OutboxEvent
from app.storage.db import Session


async def create(
    owner_uid: str,
    text: str,
    company_id=None,
    language: str = DEFAULT_LANGUAGE,
    generation_id: uuid.UUID | None = None,
    kind: str = GenerationKind.INTERVIEW,
) -> Generation:
    async with Session() as session:
        generation = Generation(
            id=generation_id or uuid.uuid4(),
            owner_uid=owner_uid,
            kind=kind,
            company_id=company_id,
            text=text,
            language=language,
            status=Status.QUEUED,
        )
        session.add(generation)
        await session.commit()

        return generation


async def get(generation_id: uuid.UUID) -> Generation | None:
    async with Session() as session:
        return await session.get(Generation, generation_id)


async def update(generation_id: uuid.UUID, event: tuple[str, dict] | None = None, **values) -> bool:
    """Never touches a finished (done or cancelled) generation, so a job still running can't
    bring it back or move it on. An `event` is saved with the change, for the outbox to publish.
    False when nothing changed."""
    async with Session() as session:
        result = await session.execute(
            sql_update(Generation)
            .where(Generation.id == generation_id, Generation.status.not_in(FINISHED))
            .values(**values)
        )

        if event and result.rowcount:
            outbox.add(session, OutboxEvent, *event)

        await session.commit()

        return result.rowcount == 1


async def claim_run(generation_id: uuid.UUID) -> bool:
    """Atomically moves a queued generation to running; False when it isn't queued (cancelled,
    failed, or claimed by another delivery of its job), so a job never runs twice."""
    async with Session() as session:
        result = await session.execute(
            sql_update(Generation)
            .where(Generation.id == generation_id, Generation.status == Status.QUEUED)
            .values(status=Status.RUNNING, error=None)
        )
        await session.commit()

        return result.rowcount == 1


async def cancel(generation_id: uuid.UUID) -> bool:
    """Atomically cancel a generation that hasn't finished; False if it already has."""
    async with Session() as session:
        result = await session.execute(
            sql_update(Generation)
            .where(
                Generation.id == generation_id,
                Generation.status.not_in(FINISHED),
            )
            .values(status=Status.CANCELLED)
        )
        await session.commit()

        return result.rowcount == 1


async def fail_stuck(running_before: datetime, queued_before: datetime, error: str) -> list:
    """Marks generations running untouched since `running_before`, or queued since
    `queued_before`, as failed; returns them. A queued one may only be waiting for the queue,
    so it gets longer."""
    async with Session() as session:
        failed = await session.scalars(
            sql_update(Generation)
            .where(
                or_(
                    and_(
                        Generation.status == Status.RUNNING, Generation.updated_at < running_before
                    ),
                    and_(Generation.status == Status.QUEUED, Generation.updated_at < queued_before),
                )
            )
            .values(status=Status.FAILED, error=error)
            .returning(Generation)
        )
        failed = list(failed)
        await session.commit()

        return failed


async def expire_reviews(before: datetime) -> list[Generation]:
    """Cancels generations awaiting review since before `before`; returns them."""
    async with Session() as session:
        expired = await session.scalars(
            sql_update(Generation)
            .where(Generation.status == Status.AWAITING_REVIEW, Generation.updated_at < before)
            .values(status=Status.CANCELLED)
            .returning(Generation)
        )
        expired = list(expired)

        # Companies removes the interview of an expired review.
        for generation in expired:
            if generation.kind != GenerationKind.INTERVIEW:
                continue

            outbox.add(
                session,
                OutboxEvent,
                GENERATION_CANCELLED,
                {"generation_id": str(generation.id)},
            )

        await session.commit()

        return expired


async def finished_threads() -> list[str]:
    """Checkpoint threads of done or cancelled generations; nothing resumes them."""
    query = text(
        "SELECT DISTINCT c.thread_id FROM checkpoints c "
        "JOIN generations g ON c.thread_id = g.id::text "
        "WHERE g.status IN :statuses"
    ).bindparams(bindparam("statuses", list(FINISHED), expanding=True, type_=String()))

    async with Session() as session:
        return list(await session.scalars(query))


async def is_cancelled(generation_id: uuid.UUID) -> bool:
    async with Session() as session:
        status = await session.scalar(
            select(Generation.status).where(Generation.id == generation_id)
        )

    return status == Status.CANCELLED


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
