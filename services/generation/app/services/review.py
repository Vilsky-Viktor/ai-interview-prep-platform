from fastapi import HTTPException, status

from app.models.generation import Generation
from app.schemas.generation import ReviewRequest
from app.storage import generations


async def submit_review(arq, generation: Generation, body: ReviewRequest) -> Generation:
    """Queues the reviewed topics; only one review wins for a generation awaiting review."""
    if not await generations.claim_review(generation.id):
        raise HTTPException(status.HTTP_409_CONFLICT, "Generation is not awaiting review")

    await arq.enqueue_job("run_generation", str(generation.id), body.model_dump())

    return await generations.get(generation.id)
