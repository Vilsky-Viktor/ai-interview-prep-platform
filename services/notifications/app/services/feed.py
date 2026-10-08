import asyncio
import json
from collections.abc import AsyncIterator

from prepza_common.notifications import Recipient

from app.constants.notifications import CHANNEL, DROPDOWN_LIMIT, HEARTBEAT_SECONDS
from app.integrations import companies
from app.integrations.redis import get_redis
from app.integrations.subscription import listening
from app.schemas.notifications import FeedOut, NotificationOut
from app.storage import notifications
from app.storage.notifications import Recipients


async def recipients_of(user_id: str) -> Recipients:
    """The user's own notifications, and those of every company they belong to."""
    ids = await companies.company_ids(user_id)

    return [(Recipient.USER, user_id), *((Recipient.COMPANY, company_id) for company_id in ids)]


async def feed(user_id: str) -> FeedOut:
    recipients = await recipients_of(user_id)
    items = await notifications.latest(recipients, DROPDOWN_LIMIT)

    return FeedOut(
        items=[NotificationOut.model_validate(item) for item in items],
        unread=await notifications.unread_count(recipients, user_id),
    )


async def announce(recipient: str, recipient_id: str) -> None:
    """Tells the recipient's open tabs, on any instance, that something new came."""
    channel = CHANNEL.format(recipient=recipient, recipient_id=recipient_id)
    await get_redis().publish(channel, "new")


async def changes(user_id: str) -> AsyncIterator[str]:
    """Server-sent events for one open tab: {"new": true} whenever one of the user's recipients
    gets a notification, and a comment every HEARTBEAT_SECONDS so the connection stays open. The
    instance's tabs share one Redis subscription."""
    recipients = await recipients_of(user_id)
    channels = [CHANNEL.format(recipient=kind, recipient_id=id_) for kind, id_ in recipients]

    async with listening(channels) as heard:
        yield ": connected\n\n"

        while True:
            try:
                await asyncio.wait_for(heard.wait(), HEARTBEAT_SECONDS)
            except TimeoutError:
                yield ": heartbeat\n\n"

                continue

            heard.clear()

            yield f"data: {json.dumps({'new': True})}\n\n"
