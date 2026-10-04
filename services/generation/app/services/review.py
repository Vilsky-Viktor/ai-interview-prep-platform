from fastapi import HTTPException, status

from app.constants.generation import FREE_KIT_TOO_MANY_TOPICS, RUN_GENERATION
from app.helpers.topics import too_many_for_free_kit
from app.integrations import tasks
from app.models.generation import Generation
from app.schemas.generation import ReviewRequest
from app.storage import generations


async def submit_review(generation: Generation, body: ReviewRequest) -> Generation:
    """Queues the reviewed topics; only one review wins for a generation awaiting review."""
    if too_many_for_free_kit(generation.free_kit, body.model_dump()):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, FREE_KIT_TOO_MANY_TOPICS)

    if not await generations.claim_review(generation.id):
        raise HTTPException(status.HTTP_409_CONFLICT, "Generation is not awaiting review")

    await tasks.enqueue(
        RUN_GENERATION, {"generation_id": str(generation.id), "resume": body.model_dump()}
    )

    return await generations.get(generation.id)
