from datetime import datetime

from sqlalchemy import exists, select
from sqlalchemy.orm import selectinload

from app.models.companies import Company
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.storage.db import Session


async def with_members(company_ids: list) -> list[Company]:
    """The companies of those ids that still exist, with their members."""
    if not company_ids:
        return []

    query = (
        select(Company).where(Company.id.in_(company_ids)).options(selectinload(Company.members))
    )

    async with Session() as session:
        return list(await session.scalars(query))


async def without_candidates(ready_after: datetime, ready_before: datetime) -> list[Interview]:
    """Interviews that got their questions between those times, nobody was invited to, and
    that aren't marked hired."""
    invited = exists().where(CandidateInvite.interview_id == Interview.id)
    query = select(Interview).where(
        Interview.ready_at > ready_after,
        Interview.ready_at <= ready_before,
        Interview.hired.is_(False),
        ~invited,
    )

    async with Session() as session:
        return list(await session.scalars(query))


async def being_generated(started_after: datetime, started_before: datetime) -> list[Interview]:
    """Interviews started between those times still waiting for their questions: their
    generation may be waiting for its topics' review."""
    query = select(Interview).where(
        Interview.created_at > started_after,
        Interview.created_at <= started_before,
        Interview.generation_id.is_not(None),
        Interview.set_id.is_(None),
        Interview.generation_failed.is_(False),
    )

    async with Session() as session:
        return list(await session.scalars(query))
