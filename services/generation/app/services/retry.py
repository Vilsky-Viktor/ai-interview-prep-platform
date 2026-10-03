from fastapi import HTTPException, status

from app.constants.generation import RUN_GENERATION
from app.constants.kinds import GenerationKind
from app.integrations import billing, tasks
from app.models.generation import Generation
from app.storage import generations


async def retry_generation(generation: Generation) -> Generation:
    """Queues a failed generation again; the worker continues from its last checkpoint."""
    if generation.kind == GenerationKind.PREPARATION:
        await billing.hold_kit(generation.owner_uid, generation.id)

    if not await generations.claim_retry(generation.id):
        if generation.kind == GenerationKind.PREPARATION:
            await billing.release_kit(generation.id)

        raise HTTPException(status.HTTP_409_CONFLICT, "Only a failed generation can be retried")

    await tasks.enqueue(RUN_GENERATION, {"generation_id": str(generation.id)})

    return await generations.get(generation.id)
