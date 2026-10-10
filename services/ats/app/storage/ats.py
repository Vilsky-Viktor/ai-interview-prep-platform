from uuid import UUID

from prepza_common.constants import DELETED_USER
from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert

from app.constants.ats import ConnectionStatus
from app.models.ats import AtsCandidate, AtsConnection, AtsJobLink
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


async def connection_by_id(connection_id: UUID) -> AtsConnection | None:
    async with Session() as session:
        return await session.get(AtsConnection, connection_id)


async def connect(
    company_id: UUID,
    provider: str,
    account: str,
    credentials: str,
    user_id: str,
    member_id: str | None = None,
    user_name: str | None = None,
) -> None:
    """Saves the company's connection to `provider`, replacing an earlier one's key (a
    reconnect keeps its linked jobs)."""
    values = {
        "account": account,
        "credentials": credentials,
        "status": ConnectionStatus.CONNECTED,
        "created_by": user_id,
        "created_by_name": user_name,
        "member_id": member_id,
    }
    query = (
        insert(AtsConnection)
        .values(company_id=company_id, provider=provider, **values)
        .on_conflict_do_update(index_elements=["company_id", "provider"], set_=values)
    )

    async with Session() as session:
        await session.execute(query)
        await session.commit()


async def set_credentials(connection_id: UUID, credentials: str) -> None:
    """Replaces the connection's sealed credentials (a web hook's signature key added)."""
    query = (
        update(AtsConnection)
        .where(AtsConnection.id == connection_id)
        .values(credentials=credentials)
    )

    async with Session() as session:
        await session.execute(query)
        await session.commit()


async def restore_broken(earlier: AtsConnection) -> None:
    """Puts back a connection as it was before a reconnect that failed (its key, account, maker
    and member), marked for reconnecting: its linked jobs and candidates stay."""
    query = (
        update(AtsConnection)
        .where(AtsConnection.id == earlier.id)
        .values(
            account=earlier.account,
            credentials=earlier.credentials,
            created_by=earlier.created_by,
            created_by_name=earlier.created_by_name,
            member_id=earlier.member_id,
            status=ConnectionStatus.BROKEN,
        )
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


async def made_by(user_id: str) -> list[AtsConnection]:
    query = select(AtsConnection).where(AtsConnection.created_by == user_id)

    async with Session() as session:
        return list(await session.scalars(query))


async def forget_maker(user_id: str) -> None:
    """The connections the user made stay with their companies, without the user's id, and
    stop inviting, as when their maker stops being an editor: an editor reconnects them."""
    query = (
        update(AtsConnection)
        .where(AtsConnection.created_by == user_id)
        .values(created_by=DELETED_USER, status=ConnectionStatus.BROKEN)
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


async def links(company_id: UUID) -> list[tuple[AtsJobLink, str]]:
    """The company's linked jobs, newest first, each with its ATS."""
    query = (
        select(AtsJobLink, AtsConnection.provider)
        .join(AtsConnection, AtsConnection.id == AtsJobLink.connection_id)
        .where(AtsConnection.company_id == company_id)
        .order_by(AtsJobLink.created_at.desc())
    )

    async with Session() as session:
        return [tuple(row) for row in (await session.execute(query)).all()]


async def add_link(connection_id: UUID, interview_id: UUID, job: dict, stage: dict) -> UUID | None:
    """Links a job to an interview: the link's id, or None when that job is already linked."""
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

    return added


async def set_subscription(link_id: UUID, subscription_id: str) -> None:
    query = (
        update(AtsJobLink).where(AtsJobLink.id == link_id).values(subscription_id=subscription_id)
    )

    async with Session() as session:
        await session.execute(query)
        await session.commit()


async def link(link_id: UUID) -> tuple[AtsJobLink, AtsConnection] | None:
    """A linked job with its connection: where an ATS event for it is checked."""
    query = (
        select(AtsJobLink, AtsConnection)
        .join(AtsConnection, AtsConnection.id == AtsJobLink.connection_id)
        .where(AtsJobLink.id == link_id)
    )

    async with Session() as session:
        row = (await session.execute(query)).first()

        return tuple(row) if row else None


async def interview_links(interview_id: UUID) -> list[tuple[AtsJobLink, AtsConnection]]:
    """The jobs linked to an interview, each with its connection: what to cancel in the ATS
    when the interview goes."""
    query = (
        select(AtsJobLink, AtsConnection)
        .join(AtsConnection, AtsConnection.id == AtsJobLink.connection_id)
        .where(AtsJobLink.interview_id == interview_id)
    )

    async with Session() as session:
        return [tuple(row) for row in (await session.execute(query)).all()]


async def link_for_job(connection_id: UUID, job_id: str) -> AtsJobLink | None:
    query = select(AtsJobLink).where(
        AtsJobLink.connection_id == connection_id, AtsJobLink.job_id == job_id
    )

    async with Session() as session:
        return await session.scalar(query)


async def has_links(connection_id: UUID) -> bool:
    query = select(AtsJobLink.id).where(AtsJobLink.connection_id == connection_id).limit(1)

    async with Session() as session:
        return await session.scalar(query) is not None


async def subscriptions(company_id: UUID, link_id: UUID | None = None) -> list[str]:
    """The ATS notifications of the company's linked jobs (or of one), to cancel them."""
    query = (
        select(AtsJobLink.subscription_id)
        .join(AtsConnection, AtsConnection.id == AtsJobLink.connection_id)
        .where(AtsConnection.company_id == company_id, AtsJobLink.subscription_id.is_not(None))
    )

    if link_id is not None:
        query = query.where(AtsJobLink.id == link_id)

    async with Session() as session:
        return list((await session.scalars(query)).all())


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


async def delete_interview(interview_id: UUID) -> None:
    """An interview was deleted: its linked jobs and the candidates sent for it go."""
    async with Session() as session:
        await session.execute(delete(AtsCandidate).where(AtsCandidate.interview_id == interview_id))
        await session.execute(delete(AtsJobLink).where(AtsJobLink.interview_id == interview_id))
        await session.commit()


async def delete_company(company_id: UUID) -> None:
    """A company was deleted: its connections go, with their linked jobs and candidates."""
    async with Session() as session:
        await session.execute(delete(AtsConnection).where(AtsConnection.company_id == company_id))
        await session.commit()
