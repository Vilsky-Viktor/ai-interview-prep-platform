import logging
from uuid import UUID

from fastapi import HTTPException
from prepza_common.constants import DAY_SECONDS, HOUR_SECONDS
from prepza_common.rate_limit import hit, spend

from app.constants.limits import (
    MESSAGES_PER_COMPANY_DAY,
    MESSAGES_PER_DAY,
    MESSAGES_PER_USER_DAY,
    MESSAGES_PER_USER_HOUR,
    TOKENS_PER_COMPANY_DAY,
    TOKENS_PER_DAY,
    TOKENS_PER_USER_DAY,
    TRANSCRIPTIONS_PER_USER_HOUR,
)

logger = logging.getLogger(__name__)


def budgets(user_id: str, company_id: UUID | None) -> list[tuple[str, int]]:
    """The spending budgets a turn counts against: the user's, their company's and everyone's."""
    found = [(f"spend:assistant:user:{user_id}", TOKENS_PER_USER_DAY)]

    if company_id is not None:
        found.append((f"spend:assistant:company:{company_id}", TOKENS_PER_COMPANY_DAY))

    return [*found, ("spend:assistant:all", TOKENS_PER_DAY)]


async def check_budgets(redis, user_id: str, company_id: UUID | None) -> None:
    """Refuses (429) once a budget is spent."""
    for key, budget in budgets(user_id, company_id):
        await spend(redis, key, 0, budget, DAY_SECONDS)


async def check(redis, user_id: str, company_id: UUID | None) -> None:
    """Counts one message, and refuses it (429) over a message limit or a spent budget."""
    await check_budgets(redis, user_id, company_id)
    await hit(redis, f"rate:assistant:hour:{user_id}", MESSAGES_PER_USER_HOUR, HOUR_SECONDS)
    await hit(redis, f"rate:assistant:day:{user_id}", MESSAGES_PER_USER_DAY, DAY_SECONDS)

    if company_id is not None:
        key = f"rate:assistant:company:{company_id}"
        await hit(redis, key, MESSAGES_PER_COMPANY_DAY, DAY_SECONDS)

    await hit(redis, "rate:assistant:all", MESSAGES_PER_DAY, DAY_SECONDS)


async def check_transcription(redis, user_id: str) -> None:
    """Counts one voice message, and refuses it (429) over the user's hourly limit or a spent
    budget. Its transcript is then sent as a message, which counts as one."""
    await check_budgets(redis, user_id, None)
    key = f"rate:assistant:transcribe:hour:{user_id}"
    await hit(redis, key, TRANSCRIPTIONS_PER_USER_HOUR, HOUR_SECONDS)


async def record(redis, user_id: str, company_id: UUID | None, tokens: int) -> None:
    """Adds a finished turn's tokens to its budgets. Going over refuses the next message, not
    this one; with Redis down, the turn's spending is lost rather than the answer."""
    for key, budget in budgets(user_id, company_id):
        try:
            await spend(redis, key, tokens, budget, DAY_SECONDS)
        except HTTPException:
            pass
        except Exception:
            logger.warning("Couldn't add a turn's tokens to %s", key, exc_info=True)
