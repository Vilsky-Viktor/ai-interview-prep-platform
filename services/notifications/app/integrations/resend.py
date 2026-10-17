from fastapi import status
from prepza_common import http
from prepza_common.http import bearer
from prepza_common.limits import record_hit

from app.config.settings import settings
from app.constants.email import (
    RESEND_DAILY_QUOTA_ERROR,
    RESEND_EMAILS_URL,
    RESEND_REFUSED,
    SEND_TIMEOUT_S,
)
from app.models.email import Email


class EmailRefused(Exception):
    """Resend won't ever send this email; retrying is pointless."""


class ResendBusy(Exception):
    """Over Resend's per-second limit (a burst of invites) or its daily quota: nothing was sent,
    a retry will."""


def quota_used(response) -> bool:
    """Whether Resend's 429 is for its daily quota rather than its per-second limit: its error's
    name says so."""
    try:
        return response.json().get("name") == RESEND_DAILY_QUOTA_ERROR
    except ValueError:
        return False


async def send(email: Email, idempotency_key: str) -> None:
    """Sends through Resend, on the service's shared connections; the same key within 24 hours
    never sends twice, so retries are safe."""
    response = await http.get_client().post(
        RESEND_EMAILS_URL,
        headers={**bearer(settings.resend_api_key), "Idempotency-Key": idempotency_key},
        json={
            "from": settings.mail_from_updates if email.optional else settings.mail_from,
            "to": [email.to],
            "subject": email.subject,
            "html": email.html,
            "text": email.text,
            "tags": [{"name": name, "value": value} for name, value in email.tags.items()],
            "reply_to": email.reply_to or settings.contact_email,
            "headers": email.headers,
            **(
                {
                    "attachments": [
                        {"filename": name, "content": content}
                        for name, content in email.attachments
                    ]
                }
                if email.attachments
                else {}
            ),
        },
        timeout=SEND_TIMEOUT_S,
    )

    if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        name = "RESEND_DAILY_QUOTA" if quota_used(response) else "RESEND_RATE_LIMIT"
        await record_hit(name, kind="provider:resend", scope="everyone")

        raise ResendBusy()

    if response.status_code in RESEND_REFUSED:
        raise EmailRefused(f"Resend refused the email ({response.status_code}): {response.text}")

    if response.is_error:
        raise RuntimeError(f"Resend refused the email ({response.status_code}): {response.text}")
