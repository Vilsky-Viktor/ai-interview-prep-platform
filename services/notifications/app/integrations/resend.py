import httpx

from app.config.settings import settings
from app.constants.email import RESEND_EMAILS_URL, RESEND_REFUSED, SEND_TIMEOUT_S
from app.models.email import Email


class EmailRefused(Exception):
    """Resend won't ever send this email; retrying is pointless."""


async def send(email: Email, idempotency_key: str) -> None:
    """Sends through Resend; the same key within 24 hours never sends twice, so retries are safe."""
    async with httpx.AsyncClient(timeout=SEND_TIMEOUT_S) as client:
        response = await client.post(
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
            },
        )

    if response.status_code in RESEND_REFUSED:
        raise EmailRefused(f"Resend refused the email ({response.status_code}): {response.text}")

    if response.is_error:
        raise RuntimeError(f"Resend refused the email ({response.status_code}): {response.text}")
