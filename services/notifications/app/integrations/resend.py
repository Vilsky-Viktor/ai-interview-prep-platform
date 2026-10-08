from fastapi import status
from prepza_common import http

from app.config.settings import settings
from app.constants.email import RESEND_EMAILS_URL, RESEND_REFUSED, SEND_TIMEOUT_S
from app.models.email import Email


class EmailRefused(Exception):
    """Resend won't ever send this email; retrying is pointless."""


class ResendBusy(Exception):
    """Over Resend's per-second limit (a burst of invites): nothing was sent, a retry will."""


async def send(email: Email, idempotency_key: str) -> None:
    """Sends through Resend, on the service's shared connections; the same key within 24 hours
    never sends twice, so retries are safe."""
    response = await http.get_client().post(
        RESEND_EMAILS_URL,
        headers={
            "Authorization": f"Bearer {settings.resend_api_key}",
            "Idempotency-Key": idempotency_key,
        },
        json={
            "from": settings.mail_from,
            "to": [email.to],
            "subject": email.subject,
            "html": email.html,
            "text": email.text,
            "tags": [{"name": name, "value": value} for name, value in email.tags.items()],
            **({"reply_to": email.reply_to} if email.reply_to else {}),
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
        raise ResendBusy()

    if response.status_code in RESEND_REFUSED:
        raise EmailRefused(f"Resend refused the email ({response.status_code}): {response.text}")

    if response.is_error:
        raise RuntimeError(f"Resend refused the email ({response.status_code}): {response.text}")
