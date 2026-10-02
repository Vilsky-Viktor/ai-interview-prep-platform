import httpx

from app.config.settings import settings
from app.constants.email import RESEND_EMAILS_URL, SEND_TIMEOUT_S
from app.models.email import Email


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
            },
        )

    if response.is_error:
        raise RuntimeError(f"Resend refused the email ({response.status_code}): {response.text}")
