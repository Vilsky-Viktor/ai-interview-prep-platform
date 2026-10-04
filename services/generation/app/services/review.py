from fastapi import HTTPException, status

from app.constants.generation import RUN_GENERATION
from app.constants.kinds import GenerationKind
from app.constants.statuses import Status
from app.helpers.topics import approves
from app.integrations import billing, tasks
from app.models.generation import Generation
from app.schemas.generation import ReviewRequest
from app.services.budget import use_daily_budget
from app.storage import generations


async def pay_for_kit(generation: Generation) -> None:
    """A learner's kit is paid when its topics are approved: drafting them is free. Credits first,
    so a refused approval never uses up the day's cap for everyone."""
    await billing.hold_kit(generation.owner_uid, generation.id)

    try:
        await use_daily_budget()
    except HTTPException:
        await billing.release_kit(generation.id)
        raise


async def submit_review(generation: Generation, body: ReviewRequest) -> Generation:
    """Queues the reviewed topics; only one review wins for a generation awaiting review.

    Approving a learner's kit sets its credits aside; without enough, the draft waits for a
    top-up. Revising with instructions is free."""
    approving = approves(body.model_dump())

    if not await generations.claim_review(generation.id):
        raise HTTPException(status.HTTP_409_CONFLICT, "Generation is not awaiting review")

    if approving and generation.kind == GenerationKind.PREPARATION:
        try:
            await pay_for_kit(generation)
        except HTTPException:
            # Back to review, so the learner can approve again after topping up.
            await generations.update(generation.id, status=Status.AWAITING_REVIEW)
            raise

    if approving:
        await generations.update(generation.id, approved=True)

    await tasks.enqueue(
        RUN_GENERATION, {"generation_id": str(generation.id), "resume": body.model_dump()}
    )

    return await generations.get(generation.id)
