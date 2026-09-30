import asyncio
import smtplib
from email.message import EmailMessage

from app.config.settings import settings


def send_sync(message: EmailMessage) -> None:
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as client:
        client.send_message(message)


async def send(message: EmailMessage) -> None:
    await asyncio.to_thread(send_sync, message)
