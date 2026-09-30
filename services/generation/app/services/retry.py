from fastapi import HTTPException, status

from app.models.generation import Generation
from app.storage import generations


async def retry_generation(arq, generation: Generation) -> Generation:
    """Queues a failed generation again; the worker continues from its last checkpoint."""
    if not await generations.claim_retry(generation.id):
        raise HTTPException(status.HTTP_409_CONFLICT, "Only a failed generation can be retried")

    await arq.enqueue_job("run_generation", str(generation.id))

    return await generations.get(generation.id)
