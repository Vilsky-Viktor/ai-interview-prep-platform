import asyncio
import base64
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

    for name, value in email.headers.items():
        message[name] = value

    message.set_content(email.text)
    message.add_alternative(email.html, subtype="html")

    for name, content in email.attachments:
        message.add_attachment(
            base64.b64decode(content), maintype="application", subtype="pdf", filename=name
        )

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=SEND_TIMEOUT_S) as client:
        client.send_message(message)


async def send(email: Email) -> None:
    await asyncio.to_thread(send_sync, email)
