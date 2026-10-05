from datetime import UTC, datetime, timedelta

from app.constants.invites import REMINDER_AFTER_DAYS
from app.services import outbox as outbox_service
from app.storage import reminders


async def remind_unstarted() -> int:
    """Reminds candidates who haven't started REMINDER_AFTER_DAYS after their invite, once."""
    count = await reminders.remind_unstarted(
        datetime.now(UTC) - timedelta(days=REMINDER_AFTER_DAYS)
    )
    await outbox_service.flush_quietly()

    return count
