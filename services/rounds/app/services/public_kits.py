from datetime import UTC, datetime, time

from fastapi import HTTPException, status
from prepza_common.analytics import track
from prepza_common.constants import PUBLIC_TOPICS_PER_DAY

from app.constants.rounds import PUBLIC_TOPICS_LIMIT
from app.schemas.library import TopicQuestions
from app.storage import rounds


async def check_daily_limit(user_id: str, topic: TopicQuestions) -> None:
    """Starting a new topic of someone else's public kit counts towards the day's limit;
    continuing one already started never does."""
    if topic.public_author_id is None or await rounds.has_started(user_id, topic.id):
        return

    midnight = datetime.combine(datetime.now(UTC).date(), time(), tzinfo=UTC)

    if await rounds.public_topics_started_since(user_id, midnight) >= PUBLIC_TOPICS_PER_DAY:
        await track("limit_hit", user_id=user_id, which="public_topics_a_day")

        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, PUBLIC_TOPICS_LIMIT)
