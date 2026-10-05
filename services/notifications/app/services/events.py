import logging

from app.config.settings import settings
from app.constants.events import (
    CANDIDATE_INVITED,
    CANDIDATE_REMINDED,
    CONTACT_SENT,
    NOTIFICATION_REQUESTED,
    REPORT_SHARED,
)
from app.helpers.emails import (
    candidate_invite_email,
    candidate_reminder_email,
    contact_email,
    report_email,
)
from app.integrations import resend, smtp
from app.models.email import Email
from app.services.feed import announce
from app.services.webhooks import report_undelivered
from app.storage import notifications

logger = logging.getLogger(__name__)


async def deliver(email: Email, message_id: str) -> None:
    if settings.resend_api_key:
        # Pub/Sub's message id as the key, so a retried event never sends the email twice.
        try:
            await resend.send(email, f"events/{message_id}")
        except resend.EmailRefused:
            # Final, like a bounce: the invite shows as undelivered and the event isn't retried.
            logger.warning("Email for %s refused", email.tags or "an untagged event", exc_info=True)
            await report_undelivered(email.tags)

        return

    await smtp.send(email)


async def notify(data: dict, message_id: str) -> None:
    """Stores a requested notification and tells the recipient's open tabs. A retried event is
    stored once and announced once; if announcing fails, the tabs see it on their next load."""
    if not await notifications.add(message_id, data):
        return

    try:
        await announce(data["recipient"], data["recipient_id"])
    except Exception:
        logger.exception("Couldn't announce a %s notification", data["kind"])


async def handle(event_type: str, data: dict, message_id: str) -> None:
    """Sends the email or stores the notification an event asks for; other events aren't ours."""
    if event_type == NOTIFICATION_REQUESTED:
        await notify(data, message_id)

    if event_type == CANDIDATE_INVITED:
        await deliver(candidate_invite_email(data, settings.site_url), message_id)

    if event_type == CANDIDATE_REMINDED:
        await deliver(candidate_reminder_email(data, settings.site_url), message_id)

    if event_type == REPORT_SHARED:
        await deliver(report_email(data, settings.site_url), message_id)

    if event_type == CONTACT_SENT:
        await deliver(contact_email(data, settings.contact_email), message_id)
