from fastapi import HTTPException, status

from app.constants.generation import RUN_GENERATION
from app.constants.kinds import GenerationKind
from app.integrations import billing, tasks
from app.models.generation import Generation
from app.storage import generations


async def retry_generation(generation: Generation) -> Generation:
    """Queues a failed generation again; the worker continues from its last checkpoint. A kit
    that failed after its topics were approved gave its credits back, so it sets them aside
    again; one that failed before, while drafting, is still free."""
    paid = generation.kind == GenerationKind.PREPARATION and generation.approved

    if paid:
        await billing.hold_kit(generation.owner_uid, generation.id)

    if not await generations.claim_retry(generation.id):
        if paid:
            await billing.release_kit(generation.id)

        raise HTTPException(status.HTTP_409_CONFLICT, "Only a failed generation can be retried")

    await tasks.enqueue(RUN_GENERATION, {"generation_id": str(generation.id)})

    return await generations.get(generation.id)
