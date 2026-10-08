from datetime import UTC, datetime, timedelta

from prepza_common.constants import DELETED_USER
from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert

from app.constants.notifications import EXPIRED_PER_PRUNE, KEEP_DAYS
from app.constants.slack import SlackStatus
from app.models.slack import SlackConnection, SlackPost
from app.storage.db import Session


async def get(company_id: str) -> SlackConnection | None:
    async with Session() as session:
        return await session.get(SlackConnection, company_id)


async def tokens() -> list[str]:
    """Every company's sealed token: companies on one workspace share it."""
    async with Session() as session:
        return list(await session.scalars(select(SlackConnection.token)))


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


async def made_by(user_id: str) -> list[SlackConnection]:
    query = select(SlackConnection).where(SlackConnection.created_by == user_id)

    async with Session() as session:
        return list(await session.scalars(query))


async def forget_maker(user_id: str) -> None:
    """The channels the user connected stay with their companies, without the user's id, and
    stop working, as when their maker stops being an editor: an editor reconnects them."""
    query = (
        update(SlackConnection)
        .where(SlackConnection.created_by == user_id)
        .values(created_by=DELETED_USER, status=SlackStatus.BROKEN)
    )

    async with Session() as session:
        await session.execute(query)
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


async def claim(key: str) -> bool:
    """Marks the notification `key` as posted to Slack; False when it already was (or is being
    posted right now), so a retried or duplicate event posts it once. Expired marks go, at most
    EXPIRED_PER_PRUNE a call, long after Pub/Sub stops redelivering (7 days)."""
    now = datetime.now(UTC)
    expired = (
        select(SlackPost.event_id)
        .where(SlackPost.posted_at < now - timedelta(days=KEEP_DAYS))
        .limit(EXPIRED_PER_PRUNE)
        .with_for_update(skip_locked=True)
    )

    async with Session() as session:
        await session.execute(delete(SlackPost).where(SlackPost.event_id.in_(expired)))
        claimed = await session.scalar(
            insert(SlackPost)
            .values(event_id=key, posted_at=now)
            .on_conflict_do_nothing(index_elements=["event_id"])
            .returning(SlackPost.event_id)
        )
        await session.commit()

    return claimed is not None


async def release(key: str) -> None:
    """Slack didn't take the notification `key`: the event's retry may post it."""
    async with Session() as session:
        await session.execute(delete(SlackPost).where(SlackPost.event_id == key))
        await session.commit()
