import logging
from datetime import UTC, datetime, timedelta

from app.constants.accounts import TEXT_RETENTION_DAYS
from app.constants.generation import GENERATION_STOPPED, REVIEW_EXPIRY_DAYS, STUCK_AFTER_SECONDS
from app.services import outbox as outbox_service
from app.services.key_check_batches import collect_finished, submit_pending
from app.storage import accounts, generations

logger = logging.getLogger(__name__)

# Cloud Scheduler calls these through routers/schedules.py; their timetable is in the
# infrastructure (and scripts/crontab locally).


async def key_check_batches() -> None:
    """Applies finished OpenAI batches of key checks, then sends the waiting ones."""
    await collect_finished()
    await submit_pending()


async def expire_reviews() -> None:
    """Cancels topic reviews left open for REVIEW_EXPIRY_DAYS; an interview's event, saved with
    the cancellation, removes it in companies."""
    before = datetime.now(UTC) - timedelta(days=REVIEW_EXPIRY_DAYS)
    await generations.expire_reviews(before)
    await outbox_service.flush_quietly()


async def sweep(checkpointer) -> None:
    """Fails generations whose worker died mid-job, so the user can Retry them, and deletes
    checkpoints nothing will resume. Failed and in-review generations keep theirs."""
    before = datetime.now(UTC) - timedelta(seconds=STUCK_AFTER_SECONDS)
    count = await generations.fail_stuck(before, GENERATION_STOPPED)

    if count:
        logger.warning("Marked %d stuck generations as failed", count)

    await expire_reviews()

    for thread_id in await generations.finished_threads():
        await checkpointer.adelete_thread(thread_id)


async def retention(checkpointer) -> None:
    """Daily: pasted job texts aren't kept longer than needed."""
    before = datetime.now(UTC) - timedelta(days=TEXT_RETENTION_DAYS)
    count = await accounts.forget_texts(before, checkpointer)

    if count:
        logger.info("Removed the pasted texts of %d old generations", count)


async def flush_outbox() -> int:
    """Every minute: publishes events that weren't published right after their change."""
    return await outbox_service.flush()
