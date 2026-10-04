from datetime import UTC, datetime, timedelta

from prepza_common.notifications import Recipient
from sqlalchemy import delete, func, select, tuple_
from sqlalchemy.dialects.postgresql import insert

from app.constants.notifications import GROUP_HOURS, GROUPED_KINDS, KEEP_DAYS, MAX_PER_RECIPIENT
from app.models.notifications import Notification, Received, Seen
from app.storage.db import Session

# (recipient, recipient_id): a user's own notifications and their companies'.
Recipients = list[tuple[str, str]]


def for_recipients(recipients: Recipients):
    return tuple_(Notification.recipient, Notification.recipient_id).in_(recipients)


async def add(event_id: str, event: dict) -> bool:
    """Stores a requested notification once, however often Pub/Sub delivers it (or, with a
    `key`, however often its producer asks); False when it was already there. A grouped kind adds
    to a recent one about the same thing instead. Then the recipient's oldest go, beyond
    MAX_PER_RECIPIENT or KEEP_DAYS."""
    now = datetime.now(UTC)
    event_id = event.get("key") or event_id

    async with Session() as session:
        # One recipient's notifications are stored one at a time, though Pub/Sub delivers in
        # parallel, so a burst still groups and the limit holds; other recipients don't wait.
        recipient = f"{event['recipient']}:{event['recipient_id']}"
        await session.execute(select(func.pg_advisory_xact_lock(func.hashtext(recipient))))
        first = await session.scalar(
            insert(Received)
            .values(event_id=event_id, received_at=now)
            .on_conflict_do_nothing(index_elements=["event_id"])
            .returning(Received.event_id)
        )

        if first is None:
            return False

        if not (event["kind"] in GROUPED_KINDS and await add_to_group(session, event, now)):
            session.add(
                Notification(
                    event_id=event_id,
                    recipient=event["recipient"],
                    recipient_id=event["recipient_id"],
                    kind=event["kind"],
                    link=event["link"],
                    data=event.get("data") or {},
                    created_at=now,
                )
            )
            await session.flush()

        await prune(session, event, now)
        await session.commit()

    return True


async def add_to_group(session, event: dict, now: datetime) -> bool:
    """Adds the event to the recipient's latest notification of its kind about the same page and
    title, if it came within GROUP_HOURS: one more in its count, the newest details, and back at
    the top as unread. False when there's none to add to."""
    data = event.get("data") or {}
    title = Notification.data["title"].astext
    group = await session.scalar(
        select(Notification)
        .where(
            Notification.recipient == event["recipient"],
            Notification.recipient_id == event["recipient_id"],
            Notification.kind == event["kind"],
            Notification.link == event["link"],
            title == data["title"] if "title" in data else title.is_(None),
            Notification.created_at > now - timedelta(hours=GROUP_HOURS),
        )
        .order_by(Notification.created_at.desc())
        .limit(1)
        .with_for_update()
    )

    if group is None:
        return False

    group.data = {**data, "count": group.data.get("count", 1) + 1}
    group.created_at = now

    return True


async def prune(session, event: dict, now: datetime) -> None:
    """The recipient keeps their newest MAX_PER_RECIPIENT; nothing is kept past KEEP_DAYS."""
    oldest_kept = now - timedelta(days=KEEP_DAYS)
    beyond_limit = (
        select(Notification.id)
        .where(
            Notification.recipient == event["recipient"],
            Notification.recipient_id == event["recipient_id"],
        )
        .order_by(Notification.created_at.desc())
        .offset(MAX_PER_RECIPIENT)
    )
    await session.execute(delete(Notification).where(Notification.id.in_(beyond_limit)))
    await session.execute(delete(Notification).where(Notification.created_at < oldest_kept))
    await session.execute(delete(Received).where(Received.received_at < oldest_kept))


async def latest(recipients: Recipients, limit: int | None) -> list[Notification]:
    """Newest first; all of them when `limit` is None."""
    async with Session() as session:
        rows = await session.scalars(
            select(Notification)
            .where(for_recipients(recipients))
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )

        return list(rows)


async def unread_count(recipients: Recipients, user_id: str) -> int:
    """Everything newer than when the user last opened the bell."""
    async with Session() as session:
        seen_at = await session.scalar(select(Seen.seen_at).where(Seen.user_id == user_id))
        query = select(func.count()).select_from(Notification).where(for_recipients(recipients))

        if seen_at is not None:
            query = query.where(Notification.created_at > seen_at)

        return await session.scalar(query) or 0


async def mark_seen(user_id: str) -> None:
    async with Session() as session:
        now = datetime.now(UTC)
        await session.execute(
            insert(Seen)
            .values(user_id=user_id, seen_at=now)
            .on_conflict_do_update(index_elements=["user_id"], set_={"seen_at": now})
        )
        await session.commit()


async def remove_user(user_id: str) -> None:
    """A deleted account takes its notifications and its seen time with it."""
    async with Session() as session:
        await session.execute(
            delete(Notification).where(
                Notification.recipient == Recipient.USER, Notification.recipient_id == user_id
            )
        )
        await session.execute(delete(Seen).where(Seen.user_id == user_id))
        await session.commit()
