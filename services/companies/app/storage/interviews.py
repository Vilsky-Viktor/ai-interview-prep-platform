import uuid

from sqlalchemy import func, select, update
from sqlalchemy.orm import selectinload

from app.models.interviews import Interview
from app.storage.db import Session


async def create(company_id, generation_id, mode: str, share_results: bool) -> Interview:
    interview = Interview(
        company_id=company_id,
        generation_id=generation_id,
        mode=mode,
        share_results=share_results,
        set_id=None,
    )

    async with Session() as session:
        session.add(interview)
        await session.commit()
        loaded = await session.get(
            Interview, interview.id, options=[selectinload(Interview.invites)]
        )

    return loaded


async def get(interview_id) -> Interview | None:
    async with Session() as session:
        return await session.get(
            Interview, interview_id, options=[selectinload(Interview.invites)]
        )


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


async def list_for_company(company_id) -> list[Interview]:
    query = (
        select(Interview)
        .where(Interview.company_id == company_id)
        .options(selectinload(Interview.invites))
        .order_by(Interview.created_at.desc())
    )

    async with Session() as session:
        return list(await session.scalars(query))


async def update_settings(interview_id, mode: str, share_results: bool) -> None:
    async with Session() as session:
        await session.execute(
            update(Interview)
            .where(Interview.id == interview_id)
            .values(mode=mode, share_results=share_results)
        )
        await session.commit()


async def set_topic_limit(interview_id, topic_id: uuid.UUID, limit: int | None) -> None:
    async with Session() as session:
        interview = await session.get(Interview, interview_id)
        limits = {key: value for key, value in interview.topic_limits.items() if key != str(topic_id)}

        if limit is not None:
            limits[str(topic_id)] = limit

        interview.topic_limits = limits
        await session.commit()


async def set_set_id(interview_id, set_id: uuid.UUID) -> None:
    async with Session() as session:
        await session.execute(
            update(Interview).where(Interview.id == interview_id).values(set_id=set_id)
        )
        await session.commit()
