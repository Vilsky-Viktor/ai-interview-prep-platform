import uuid

from prepza_common import outbox
from prepza_common.notifications import NOTIFICATION_REQUESTED
from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import selectinload

from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.models.outbox import OutboxEvent
from app.schemas.interviews import InterviewSettings
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
        loaded = await session.get(
            Interview,
            interview.id,
            options=[selectinload(Interview.invites)],
            populate_existing=True,
        )

    return loaded


async def get(interview_id) -> Interview | None:
    async with Session() as session:
        return await session.get(Interview, interview_id, options=[selectinload(Interview.invites)])


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
        .options(selectinload(Interview.invites))
        .order_by(Interview.created_at.desc(), Interview.id)
        .offset(offset)
        .limit(limit)
    )

    async with Session() as session:
        return list(await session.scalars(query))


async def update_settings(interview_id, settings: InterviewSettings) -> None:
    async with Session() as session:
        await session.execute(
            update(Interview).where(Interview.id == interview_id).values(**settings.model_dump())
        )
        await session.commit()


async def set_topic_limit(interview_id, topic_id: uuid.UUID, limit: int) -> None:
    async with Session() as session:
        interview = await session.get(Interview, interview_id)
        interview.topic_limits = {**interview.topic_limits, str(topic_id): limit}
        await session.commit()


async def remove(interview_id) -> None:
    async with Session() as session:
        await session.execute(delete(Interview).where(Interview.id == interview_id))
        await session.commit()


async def set_set_id(interview_id, set_id: uuid.UUID) -> None:
    async with Session() as session:
        await session.execute(
            update(Interview).where(Interview.id == interview_id).values(set_id=set_id)
        )
        await session.commit()


async def get_for_generation(generation_id: uuid.UUID) -> Interview | None:
    query = select(Interview).where(Interview.generation_id == generation_id)

    async with Session() as session:
        return await session.scalar(query)


async def set_generated(
    generation_id: uuid.UUID, set_id: uuid.UUID, title: str, notice: dict
) -> None:
    """Stores the set and title a finished generation produced for its interview, and the
    company's notification with them."""
    async with Session() as session:
        await session.execute(
            update(Interview)
            .where(Interview.generation_id == generation_id)
            .values(set_id=set_id, title=title)
        )
        outbox.add(session, OutboxEvent, NOTIFICATION_REQUESTED, notice)
        await session.commit()


async def remove_for_generation(generation_id: uuid.UUID, notice: dict) -> None:
    """Removes the interview of a generation that was cancelled before producing questions;
    the company's notification is saved only when one is removed."""
    async with Session() as session:
        removed = await session.scalar(
            delete(Interview)
            .where(Interview.generation_id == generation_id, Interview.set_id.is_(None))
            .returning(Interview.id)
        )

        if removed is not None:
            outbox.add(session, OutboxEvent, NOTIFICATION_REQUESTED, notice)

        await session.commit()


async def set_title(interview_id, title: str) -> None:
    async with Session() as session:
        await session.execute(
            update(Interview).where(Interview.id == interview_id).values(title=title)
        )
        await session.commit()
