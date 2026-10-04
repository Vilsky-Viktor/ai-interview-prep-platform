from fastapi import HTTPException, status

from app.constants.generation import RUN_GENERATION
from app.constants.kinds import GenerationKind
from app.integrations import billing, tasks
from app.models.generation import Generation
from app.storage import generations


async def retry_generation(generation: Generation) -> Generation:
    """Queues a failed generation again; the worker continues from its last checkpoint."""
    free_kit = False

    if generation.kind == GenerationKind.PREPARATION:
        free_kit = await billing.hold_kit(generation.owner_uid, generation.id)

    if not await generations.claim_retry(generation.id):
        if generation.kind == GenerationKind.PREPARATION:
            await billing.release_kit(generation.id)

        raise HTTPException(status.HTTP_409_CONFLICT, "Only a failed generation can be retried")

    # A failed kit gave its hold back, so the retry may be paid for differently: free again, or,
    # if the free kit went to another kit meanwhile, with credits and the full topic limit.
    if generation.kind == GenerationKind.PREPARATION and free_kit != generation.free_kit:
        await generations.update(generation.id, free_kit=free_kit)

    await tasks.enqueue(RUN_GENERATION, {"generation_id": str(generation.id)})

    return await generations.get(generation.id)
