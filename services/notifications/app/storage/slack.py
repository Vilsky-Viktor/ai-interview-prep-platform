from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert

from app.constants.slack import SlackStatus
from app.models.slack import SlackConnection
from app.storage.db import Session


async def get(company_id: str) -> SlackConnection | None:
    async with Session() as session:
        return await session.get(SlackConnection, company_id)


async def connect(
    company_id: str, team: str, channel: str, webhook: str, token: str, kinds: list, user_id: str
) -> None:
    """Saves the company's channel, replacing an earlier one; the kinds it chose stay."""
    values = {
        "team": team,
        "channel": channel,
        "webhook": webhook,
        "token": token,
        "status": SlackStatus.CONNECTED,
        "created_by": user_id,
    }
    query = (
        insert(SlackConnection)
        .values(company_id=company_id, kinds=kinds, **values)
        .on_conflict_do_update(index_elements=["company_id"], set_=values)
    )

    async with Session() as session:
        await session.execute(query)
        await session.commit()


async def set_kinds(company_id: str, kinds: list) -> None:
    query = update(SlackConnection).where(SlackConnection.company_id == company_id)

    async with Session() as session:
        await session.execute(query.values(kinds=kinds))
        await session.commit()


async def mark_broken(company_id: str) -> None:
    query = update(SlackConnection).where(SlackConnection.company_id == company_id)

    async with Session() as session:
        await session.execute(query.values(status=SlackStatus.BROKEN))
        await session.commit()


async def remove(company_id: str) -> None:
    async with Session() as session:
        await session.execute(
            delete(SlackConnection).where(SlackConnection.company_id == company_id)
        )
        await session.commit()


async def connected(company_id: str) -> SlackConnection | None:
    """The company's working channel, if any."""
    query = select(SlackConnection).where(
        SlackConnection.company_id == company_id, SlackConnection.status == SlackStatus.CONNECTED
    )

    async with Session() as session:
        return await session.scalar(query)
