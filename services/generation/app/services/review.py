from fastapi import HTTPException, status
from prepza_common.constants import DAY_SECONDS
from prepza_common.rate_limit import hit

from app.constants.generation import (
    MAX_TOPIC_REVISIONS,
    REVIEW_EXPIRY_DAYS,
    RUN_GENERATION,
    TOO_MANY_REVISIONS,
)
from app.integrations import tasks
from app.integrations.redis import get_redis
from app.models.generation import Generation
from app.schemas.generation import ReviewRequest
from app.storage import generations


async def submit_review(generation: Generation, body: ReviewRequest) -> Generation:
    """Queues the reviewed topics; only one review wins for a generation awaiting review. The
    selection must name drafted topics, and a generation's topics are revised in words (a model
    call each) at most MAX_TOPIC_REVISIONS times."""
    drafted = len(generation.topics or [])

    if any(not 0 <= index < drafted for index in body.selected):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Choose topics from the list")

    if body.instructions.strip():
        await hit(
            get_redis(),
            f"rate:revisions:{generation.id}",
            MAX_TOPIC_REVISIONS,
            REVIEW_EXPIRY_DAYS * DAY_SECONDS,
            TOO_MANY_REVISIONS,
        )

    if not await generations.claim_review(generation.id):
        raise HTTPException(status.HTTP_409_CONFLICT, "Generation is not awaiting review")

    await tasks.enqueue(
        RUN_GENERATION, {"generation_id": str(generation.id), "resume": body.model_dump()}
    )

    return await generations.get(generation.id)
