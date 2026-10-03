import uuid
from datetime import datetime

from prepza_common import outbox
from prepza_common.constants import DEFAULT_LANGUAGE
from sqlalchemy import String, bindparam, select, text
from sqlalchemy import update as sql_update

from app.constants.events import GENERATION_CANCELLED
from app.constants.kinds import GenerationKind
from app.constants.statuses import Status
from app.models.generation import Generation
from app.models.outbox import OutboxEvent
from app.storage.db import Session


async def create(
    owner_uid: str,
    text: str,
    kind: str = "preparation",
    company_id=None,
    language: str = DEFAULT_LANGUAGE,
) -> Generation:
    async with Session() as session:
        generation = Generation(
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


async def update(generation_id: uuid.UUID, event: tuple[str, dict] | None = None, **values) -> None:
    """Never touches a cancelled generation, so a job still running can't bring it back. An
    `event` is saved with the change, for the outbox to publish."""
    async with Session() as session:
        await session.execute(
            sql_update(Generation)
            .where(Generation.id == generation_id, Generation.status != Status.CANCELLED)
            .values(**values)
        )

        if event:
            outbox.add(session, OutboxEvent, *event)

        await session.commit()


async def cancel(generation_id: uuid.UUID) -> bool:
    """Atomically cancel a generation that hasn't finished; False if it already has."""
    async with Session() as session:
        result = await session.execute(
            sql_update(Generation)
            .where(
                Generation.id == generation_id,
                Generation.status.not_in([Status.DONE, Status.CANCELLED]),
            )
            .values(status=Status.CANCELLED)
        )
        await session.commit()

        return result.rowcount == 1


async def fail_stuck(before: datetime, error: str) -> int:
    """Marks queued or running generations untouched since `before` as failed; returns how many."""
    async with Session() as session:
        result = await session.execute(
            sql_update(Generation)
            .where(
                Generation.status.in_([Status.QUEUED, Status.RUNNING]),
                Generation.updated_at < before,
            )
            .values(status=Status.FAILED, error=error)
        )
        await session.commit()

        return result.rowcount


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
            if generation.kind == GenerationKind.INTERVIEW:
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
    ).bindparams(
        bindparam("statuses", [Status.DONE, Status.CANCELLED], expanding=True, type_=String())
    )

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


async def list_unfinished(owner_uid: str, offset: int, limit: int) -> list[Generation]:
    """The user's preparation generations that haven't produced a preparation or been cancelled."""
    query = (
        select(Generation)
        .where(
            Generation.owner_uid == owner_uid,
            Generation.kind == GenerationKind.PREPARATION,
            Generation.status.not_in([Status.DONE, Status.CANCELLED]),
        )
        .order_by(Generation.created_at.desc(), Generation.id)
        .offset(offset)
        .limit(limit)
    )

    async with Session() as session:
        return list(await session.scalars(query))
