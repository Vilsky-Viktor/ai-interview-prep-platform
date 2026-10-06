import logging
import uuid
from contextvars import ContextVar
from datetime import UTC, datetime, timedelta

import httpx
from prepza_common import pubsub
from prepza_common.constants import (
    HTTP_TIMEOUT_SECONDS,
    OUTBOX_BATCH,
    OUTBOX_KEEP_DAYS,
    OUTBOX_MAX_ATTEMPTS,
    OUTBOX_REJECTED_STATUSES,
    PUBLISH_IN_REQUEST_TIMEOUT_SECONDS,
)
from sqlalchemy import delete, select

logger = logging.getLogger(__name__)

# The ids of the events the current request (or job) saved, so that flush_quietly publishes
# only those and leaves older ones to the scheduled flush.
saved_ids: ContextVar[list[uuid.UUID] | None] = ContextVar("outbox_saved_ids", default=None)


def add(session, model, event_type: str, data: dict) -> None:
    """Saves an event in the caller's transaction, so it exists exactly when the change does.
    Its row id goes with it as the event's id (pubsub.EVENT_ID_ATTRIBUTE)."""
    row = model(id=uuid.uuid4(), event_type=event_type, data=data)
    session.add(row)
    saved = saved_ids.get()

    if saved is None:
        saved = []
        saved_ids.set(saved)

    saved.append(row.id)


def rejected(error: Exception) -> bool:
    """Pub/Sub refused the messages themselves, rather than being down or out of reach."""
    return (
        isinstance(error, httpx.HTTPStatusError)
        and error.response.status_code in OUTBOX_REJECTED_STATUSES
    )


def count_rejection(row, error: Exception) -> None:
    row.attempts += 1

    if row.attempts >= OUTBOX_MAX_ATTEMPTS:
        # Parked: no flush tries it again. Setting attempts back to 0 sends it once fixed.
        logger.error("Outbox event %s (%s) parked: %s", row.id, row.event_type, error)
    else:
        logger.warning("Pub/Sub rejected outbox event %s (%s): %s", row.id, row.event_type, error)


async def send(rows: list, timeout: float) -> None:
    """Publishes the rows in one call and marks them published. When Pub/Sub rejects the call,
    each row is tried alone, so only a row it won't take is counted against. Any other failure
    (an outage) raises and counts against no row."""
    messages = [pubsub.message(row.event_type, row.data, str(row.id)) for row in rows]

    try:
        await pubsub.publish_batch(messages, timeout)
    except Exception as error:
        if not rejected(error):
            raise

        if len(rows) == 1:
            count_rejection(rows[0], error)

            return

        for row in rows:
            await send([row], timeout)

        return

    now = datetime.now(UTC)

    for row in rows:
        row.published_at = now


async def flush(
    sessionmaker, model, ids: list[uuid.UUID] | None = None, timeout: float = HTTP_TIMEOUT_SECONDS
) -> int:
    """Publishes waiting events, oldest first, and returns how many; with `ids`, only those.
    Two runs never send the same row (SKIP LOCKED), and a row is locked only for its batch's
    one call. Parked rows are left out. A failure keeps the rest for the next run. The
    scheduled flush (no `ids`) also deletes published rows after OUTBOX_KEEP_DAYS."""
    query = (
        select(model)
        .where(model.published_at.is_(None), model.attempts < OUTBOX_MAX_ATTEMPTS)
        .order_by(model.created_at)
        .limit(OUTBOX_BATCH)
        .with_for_update(skip_locked=True)
    )

    if ids is not None:
        query = query.where(model.id.in_(ids))

    async with sessionmaker() as session:
        rows = list(await session.scalars(query))
        published = 0

        try:
            if rows:
                await send(rows, timeout)

            published = sum(row.published_at is not None for row in rows)
        finally:
            if ids is None:
                await session.execute(
                    delete(model).where(
                        model.published_at < datetime.now(UTC) - timedelta(days=OUTBOX_KEEP_DAYS)
                    )
                )

            await session.commit()

    return published


async def flush_quietly(sessionmaker, model) -> None:
    """Right after a change: publishes the events this request saved, at once and with a short
    timeout. A failure is only logged, as the scheduled flush sends them a minute later."""
    saved = saved_ids.get()

    if not saved:
        return

    ids = list(saved)
    saved.clear()

    try:
        await flush(sessionmaker, model, ids, PUBLISH_IN_REQUEST_TIMEOUT_SECONDS)
    except Exception:
        logger.exception("Couldn't publish waiting events; the scheduled flush will")
