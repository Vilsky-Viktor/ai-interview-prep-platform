from fastapi import HTTPException, status

from app.constants.generation import RUN_GENERATION
from app.integrations import tasks
from app.models.generation import Generation
from app.schemas.generation import ReviewRequest
from app.storage import generations


async def submit_review(generation: Generation, body: ReviewRequest) -> Generation:
    """Queues the reviewed topics; only one review wins for a generation awaiting review."""
    if not await generations.claim_review(generation.id):
        raise HTTPException(status.HTTP_409_CONFLICT, "Generation is not awaiting review")

    await tasks.enqueue(
        RUN_GENERATION, {"generation_id": str(generation.id), "resume": body.model_dump()}
    )

    return await generations.get(generation.id)
