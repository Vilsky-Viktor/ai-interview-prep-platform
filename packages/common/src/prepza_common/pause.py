# The emergency pause (internal_docs/compliance/post-market-monitoring-plan.md, section 4): a superadmin
# turns it on, and every service refuses new candidate interviews and invites, practice rounds,
# previews, AI generation and the help chat (the plan lists exactly what). Sessions already
# running may finish: answering is never refused. The switch is
# one Redis key without expiry, which every service already reads for its rate limits.
import logging

from fastapi import HTTPException, status
from prepza_common.constants import PAUSE_KEY, PAUSED

logger = logging.getLogger(__name__)


async def is_paused(redis) -> bool:
    """With Redis down, not paused: the switch must never stop the service by itself."""
    try:
        return bool(await redis.exists(PAUSE_KEY))
    except Exception:
        logger.warning("Couldn't read the pause switch; treating it as off", exc_info=True)

        return False


async def refuse_if_paused(redis) -> None:
    if await is_paused(redis):
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, PAUSED)


async def set_paused(redis, paused: bool, user_id: str) -> None:
    """Who switched it and when is kept in the logs."""
    if paused:
        await redis.set(PAUSE_KEY, user_id)
    else:
        await redis.delete(PAUSE_KEY)

    logger.warning("Emergency pause turned %s by superadmin %s", "on" if paused else "off", user_id)
