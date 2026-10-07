from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert

from app.constants.ats import ConnectionStatus
from app.models.ats import AtsConnection, AtsJobLink
from app.models.interviews import Interview
from app.storage.db import Session


async def connections(company_id: UUID) -> list[AtsConnection]:
    query = select(AtsConnection).where(AtsConnection.company_id == company_id)

    async with Session() as session:
        return list((await session.scalars(query)).all())


async def connection(company_id: UUID, provider: str) -> AtsConnection | None:
    query = select(AtsConnection).where(
        AtsConnection.company_id == company_id, AtsConnection.provider == provider
    )

    async with Session() as session:
        return await session.scalar(query)


async def connect(
    company_id: UUID, provider: str, account: str, credentials: str, user_id: str
) -> None:
    """Saves the company's connection to `provider`, replacing an earlier one's key (a
    reconnect keeps its linked jobs)."""
    values = {
        "account": account,
        "credentials": credentials,
        "status": ConnectionStatus.CONNECTED,
        "created_by": user_id,
    }
    query = (
        insert(AtsConnection)
        .values(company_id=company_id, provider=provider, **values)
        .on_conflict_do_update(index_elements=["company_id", "provider"], set_=values)
    )

    async with Session() as session:
        await session.execute(query)
        await session.commit()


async def mark_broken(connection_id: UUID) -> None:
    query = (
        update(AtsConnection)
        .where(AtsConnection.id == connection_id)
        .values(status=ConnectionStatus.BROKEN)
    )

    async with Session() as session:
        await session.execute(query)
        await session.commit()


async def disconnect(company_id: UUID, provider: str) -> None:
    """Deletes the connection and its key at once; its linked jobs go with it."""
    query = delete(AtsConnection).where(
        AtsConnection.company_id == company_id, AtsConnection.provider == provider
    )

    async with Session() as session:
        await session.execute(query)
        await session.commit()


async def links(company_id: UUID) -> list[tuple[AtsJobLink, str, str | None]]:
    """The company's linked jobs, newest first, each with its ATS and its interview's title."""
    query = (
        select(AtsJobLink, AtsConnection.provider, Interview.title)
        .join(AtsConnection, AtsConnection.id == AtsJobLink.connection_id)
        .join(Interview, Interview.id == AtsJobLink.interview_id)
        .where(AtsConnection.company_id == company_id)
        .order_by(AtsJobLink.created_at.desc())
    )

    async with Session() as session:
        return [tuple(row) for row in (await session.execute(query)).all()]


async def add_link(connection_id: UUID, interview_id: UUID, job: dict, stage: dict) -> bool:
    """Links a job to an interview; False when that job is already linked."""
    query = (
        insert(AtsJobLink)
        .values(
            connection_id=connection_id,
            interview_id=interview_id,
            job_id=job["id"],
            job_name=job["name"],
            stage_id=stage["id"],
            stage_name=stage["name"],
        )
        .on_conflict_do_nothing(index_elements=["connection_id", "job_id"])
        .returning(AtsJobLink.id)
    )

    async with Session() as session:
        added = await session.scalar(query)
        await session.commit()

    return added is not None


async def remove_link(company_id: UUID, link_id: UUID) -> bool:
    """Unlinks a job of the company; False when there's no such link."""
    owned = select(AtsConnection.id).where(AtsConnection.company_id == company_id)
    query = (
        delete(AtsJobLink)
        .where(AtsJobLink.id == link_id, AtsJobLink.connection_id.in_(owned))
        .returning(AtsJobLink.id)
    )

    async with Session() as session:
        removed = await session.scalar(query)
        await session.commit()

    return removed is not None
