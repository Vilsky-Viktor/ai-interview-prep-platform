import logging

from app.config.settings import settings
from app.integrations import resend, smtp
from app.models.email import Email
from app.services.webhooks import report_undelivered

logger = logging.getLogger(__name__)


async def send(email: Email, idempotency_key: str) -> None:
    """Through Resend when it's set up, else to the SMTP server (Mailpit). Resend never sends
    the same key twice within 24 hours, so a retry is safe. Raises resend.ResendBusy over its
    per-second limit, and on any failure a retry may fix."""
    if settings.resend_api_key:
        try:
            await resend.send(email, idempotency_key)
        except resend.EmailRefused:
            # Final, like a bounce: not retried. An invite shows as undelivered; any other email
            # (a report, a contact message, a digest) would be lost unseen, so it's an error.
            if email.tags:
                logger.warning("Email for %s refused", email.tags, exc_info=True)
            else:
                logger.exception("An untagged email was refused")

            await report_undelivered(email.tags)

        return

    await smtp.send(email)
