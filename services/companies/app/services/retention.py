import asyncio
import logging
from datetime import UTC, datetime, timedelta

from app.constants.invites import CANDIDATE_RETENTION_DAYS, RETENTION_INTERVAL_SECONDS
from app.integrations import rounds
from app.storage import accounts

logger = logging.getLogger(__name__)


async def delete_expired_candidates() -> int:
    """Candidate invites older than CANDIDATE_RETENTION_DAYS go, with the candidates' answers,
    timings and page-leave signals in rounds. Rounds first, so a failure is retried whole."""
    before = datetime.now(UTC) - timedelta(days=CANDIDATE_RETENTION_DAYS)
    invite_ids = await accounts.expired_invites(before)

    if invite_ids:
        await rounds.delete_invite_sessions(invite_ids)
        await accounts.delete_invites(invite_ids)

    return len(invite_ids)


async def keep_retaining() -> None:
    """Runs for the life of the app, next to the API (see main.py), once a day."""
    while True:
        try:
            count = await delete_expired_candidates()

            if count:
                logger.info("Deleted %d expired candidate invites", count)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Retention failed; trying again tomorrow")

        await asyncio.sleep(RETENTION_INTERVAL_SECONDS)
