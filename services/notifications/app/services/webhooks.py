import logging

from app.constants.unsubscribe import USER_SETTINGS
from app.constants.webhooks import (
    CANDIDATE_INVITE_KIND,
    COMPLAINED_EVENT,
    ID_TAG,
    KIND_TAG,
    UNDELIVERED_EVENTS,
)
from app.integrations import companies
from app.services.suppression import from_webhook
from app.services.unsubscribe import apply

logger = logging.getLogger(__name__)


async def handle(event: dict) -> None:
    """Tells the invite's owner its email wasn't delivered, turns off an optional email the user
    marked as spam, and keeps a member's address that bounced or complained off bulk sends;
    other events and untagged emails aren't ours to act on."""
    if event.get("type") not in UNDELIVERED_EVENTS:
        return

    tags = (event.get("data") or {}).get("tags") or {}
    # Counted for the bounce alert (infra/terraform/monitoring_logs.tf); no address, only its kind.
    logger.info("Email not delivered (%s): %s", event["type"], tags.get(KIND_TAG, "untagged"))

    await from_webhook(event)

    if event["type"] == COMPLAINED_EVENT:
        await complained(tags)

    await report_undelivered(tags)


async def complained(tags: dict[str, str]) -> None:
    """A spam complaint about an optional email (the digest, reminders) turns it off, as its
    unsubscribe link would: logged in library as an unsubscribe, and safe to repeat when Resend
    sends the webhook again."""
    kind, user_id = tags.get(KIND_TAG), tags.get(ID_TAG)

    if kind in USER_SETTINGS and user_id:
        await apply({"type": kind, "user_id": user_id})


async def report_undelivered(tags: dict[str, str]) -> None:
    """Marks the invite the email was for as undelivered, from its tags."""
    kind, invite_id = tags.get(KIND_TAG), tags.get(ID_TAG)

    if not invite_id:
        return

    if kind == CANDIDATE_INVITE_KIND:
        await companies.invite_undelivered(invite_id)
