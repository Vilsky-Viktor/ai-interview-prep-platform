from fastapi import HTTPException, status

from app.constants.kinds import GenerationKind
from app.integrations import billing
from app.models.generation import Generation
from app.storage import generations


async def cancel_generation(generation: Generation) -> Generation:
    """Cancels a generation that hasn't finished.

    A job already running notices at its next step and stops without saving a preparation.
    """
    if not await generations.cancel(generation.id):
        raise HTTPException(status.HTTP_409_CONFLICT, "Generation already finished")

    if generation.kind == GenerationKind.PREPARATION:
        await billing.release_kit(generation.id)

    return await generations.get(generation.id)
