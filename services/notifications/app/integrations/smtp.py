import asyncio
import smtplib
from email.message import EmailMessage

from app.config.settings import settings
from app.constants.email import SEND_TIMEOUT_S
from app.models.email import Email


def send_sync(email: Email) -> None:
    message = EmailMessage()
    message["From"] = settings.mail_from
    message["To"] = email.to
    message["Subject"] = email.subject

    if email.reply_to:
        message["Reply-To"] = email.reply_to

    message.set_content(email.text)
    message.add_alternative(email.html, subtype="html")

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=SEND_TIMEOUT_S) as client:
        client.send_message(message)


async def send(email: Email) -> None:
    await asyncio.to_thread(send_sync, email)
