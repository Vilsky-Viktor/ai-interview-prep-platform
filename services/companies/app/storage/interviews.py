import uuid

from prepza_common import outbox
from prepza_common.notifications import NOTIFICATION_REQUESTED
from sqlalchemy import delete, func, select, update

from app.constants.events import INTERVIEW_DELETED, INTERVIEW_READY
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.models.outbox import OutboxEvent
from app.schemas.interviews import InterviewSettings
from app.storage import processed_events
from app.storage.db import Session


async def create(company_id, generation_id, language: str) -> Interview:
    interview = Interview(
        company_id=company_id,
        generation_id=generation_id,
        set_id=None,
        language=language,
    )

    async with Session() as session:
        session.add(interview)
        await session.commit()

    return interview


async def create_from_template(company_id, set_id, title: str, language: str) -> Interview:
    """A test whose questions were copied from a template: ready at once, with no generation."""
    interview = Interview(
        company_id=company_id,
        generation_id=None,
        set_id=set_id,
        title=title,
        language=language,
    )

    async with Session() as session:
        session.add(interview)
        await session.commit()

    return interview


async def get_by_link(token: str) -> Interview | None:
    query = select(Interview).where(Interview.link_token == token)

    async with Session() as session:
        return await session.scalar(query)


async def set_link(interview_id, token: str | None) -> None:
    async with Session() as session:
        await session.execute(
            update(Interview).where(Interview.id == interview_id).values(link_token=token)
        )
        await session.commit()


async def get(interview_id) -> Interview | None:
    async with Session() as session:
        return await session.get(Interview, interview_id)


async def counts(company_ids: list) -> dict:
    if not company_ids:
        return {}

    query = (
        select(Interview.company_id, func.count())
        .where(Interview.company_id.in_(company_ids))
        .group_by(Interview.company_id)
    )

    async with Session() as session:
        rows = await session.execute(query)

    return {company_id: count for company_id, count in rows}


async def without_candidates(company_id) -> int:
    """The company's interviews no candidate is invited to (yet, or any more)."""
    invited = select(CandidateInvite.id).where(CandidateInvite.interview_id == Interview.id)
    query = (
        select(func.count())
        .select_from(Interview)
        .where(Interview.company_id == company_id, ~invited.exists())
    )

    async with Session() as session:
        return await session.scalar(query) or 0


async def list_for_company(
    company_id, offset: int = 0, limit: int | None = None
) -> list[Interview]:
    """Newest first; without a limit, all of them (deleting a company goes through each)."""
    query = (
        select(Interview)
        .where(Interview.company_id == company_id)
        .order_by(Interview.created_at.desc(), Interview.id)
        .offset(offset)
        .limit(limit)
    )

    async with Session() as session:
        return list(await session.scalars(query))


async def update_settings(interview_id, settings: InterviewSettings) -> None:
    """Saves the test's settings; marking it hired also turns its shareable link off, so a job
    ad left online stops bringing in candidates."""
    values = settings.model_dump()

    if settings.hired:
        values["link_token"] = None

    async with Session() as session:
        await session.execute(
            update(Interview).where(Interview.id == interview_id).values(**values)
        )
        await session.commit()


async def set_topic_limit(interview_id, topic_id: uuid.UUID, limit: int) -> None:
    async with Session() as session:
        interview = await session.get(Interview, interview_id)
        interview.topic_limits = {**interview.topic_limits, str(topic_id): limit}
        await session.commit()


async def remove(interview_id) -> None:
    """Deletes the interview, with the interview.deleted event when one is removed."""
    async with Session() as session:
        company_id = await session.scalar(
            delete(Interview).where(Interview.id == interview_id).returning(Interview.company_id)
        )

        if company_id is not None:
            add_deleted(session, interview_id, company_id)

        await session.commit()


def add_deleted(session, interview_id, company_id) -> None:
    """ats removes the deleted interview's job links and candidates."""
    data = {"interview_id": str(interview_id), "company_id": str(company_id)}
    outbox.add(session, OutboxEvent, INTERVIEW_DELETED, data)


async def set_set_id(interview_id, set_id: uuid.UUID) -> None:
    async with Session() as session:
        await session.execute(
            update(Interview)
            .where(Interview.id == interview_id)
            .values(set_id=set_id, generation_failed=False)
        )
        await session.commit()


async def get_for_generation(generation_id: uuid.UUID) -> Interview | None:
    query = select(Interview).where(Interview.generation_id == generation_id)

    async with Session() as session:
        return await session.scalar(query)


async def set_generated(
    generation_id: uuid.UUID, set_id: uuid.UUID, title: str, notice: dict, event_id: str
) -> None:
    """Stores the set and title a finished generation produced for its interview, and the
    company's notification and the interview.ready event (ats invites the candidates waiting
    for it) with them, once per event."""
    async with Session() as session:
        new = await processed_events.claim(session, event_id)
        interview_id = await session.scalar(
            update(Interview)
            .where(Interview.generation_id == generation_id)
            .values(set_id=set_id, title=title, generation_failed=False)
            .returning(Interview.id)
        )

        if new:
            outbox.add(session, OutboxEvent, NOTIFICATION_REQUESTED, notice)

        if new and interview_id is not None:
            outbox.add(session, OutboxEvent, INTERVIEW_READY, {"interview_id": str(interview_id)})

        await session.commit()


async def mark_failed(generation_id: uuid.UUID, event_id: str) -> None:
    """Marks the interview of a failed generation, once per event: a late redelivery doesn't
    mark it again after a retry. One with its questions already isn't touched."""
    async with Session() as session:
        if await processed_events.claim(session, event_id):
            await session.execute(
                update(Interview)
                .where(Interview.generation_id == generation_id, Interview.set_id.is_(None))
                .values(generation_failed=True)
            )

        await session.commit()


async def set_generation_failed(interview_id, failed: bool) -> None:
    async with Session() as session:
        await session.execute(
            update(Interview).where(Interview.id == interview_id).values(generation_failed=failed)
        )
        await session.commit()


async def remove_for_generation(generation_id: uuid.UUID, notice: dict) -> None:
    """Removes the interview of a generation that was cancelled before producing questions;
    the company's notification and the interview.deleted event are saved only when one is
    removed."""
    async with Session() as session:
        removed = (
            await session.execute(
                delete(Interview)
                .where(Interview.generation_id == generation_id, Interview.set_id.is_(None))
                .returning(Interview.id, Interview.company_id)
            )
        ).first()

        if removed is not None:
            outbox.add(session, OutboxEvent, NOTIFICATION_REQUESTED, notice)
            add_deleted(session, *removed)

        await session.commit()


async def set_title(interview_id, title: str) -> None:
    async with Session() as session:
        await session.execute(
            update(Interview).where(Interview.id == interview_id).values(title=title)
        )
        await session.commit()


async def by_ids(interview_ids: list) -> list[Interview]:
    """The interviews of those ids that still exist."""
    if not interview_ids:
        return []

    async with Session() as session:
        return list(await session.scalars(select(Interview).where(Interview.id.in_(interview_ids))))
