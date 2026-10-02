import logging
from uuid import UUID

from app.integrations import rounds

logger = logging.getLogger(__name__)


async def done_ids(user_id: str, topic_counts: dict[UUID, int]) -> set[UUID]:
    """Preparations whose every topic the user has mastered (holds a certificate for).

    Without rounds, none counts as done rather than failing the page.
    """
    if not topic_counts:
        return set()

    try:
        mastered = await rounds.mastered_counts(user_id, list(topic_counts))
    except Exception:
        logger.exception("Couldn't load mastered topics")

        return set()

    return {
        set_id
        for set_id, count in topic_counts.items()
        if count > 0 and mastered.get(str(set_id), 0) >= count
    }
