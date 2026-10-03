from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Request, status
from prepza_common.analytics import track
from prepza_common.auth import CurrentUser
from prepza_common.paging import PageParams
from prepza_common.rate_limit import hit

from app.config.settings import settings
from app.constants.generation import RUN_GENERATION
from app.constants.kinds import GenerationKind
from app.integrations import billing, tasks
from app.integrations.redis import get_redis
from app.models.generation import Generation
from app.schemas.generation import (
    GenerationCreate,
    GenerationOut,
    GenerationSummary,
    ReviewRequest,
)
from app.services.budget import use_daily_budget
from app.services.cancel import cancel_generation
from app.services.retry import retry_generation
from app.services.review import submit_review
from app.storage import generations

router = APIRouter(prefix="/generations", tags=["generations"])


async def get_owned(generation_id: UUID, user: CurrentUser) -> Generation:
    generation = await generations.get(generation_id)

    if generation is None or generation.owner_uid != user.uid:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Generation not found")

    return generation


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_generation(
    body: GenerationCreate, user: CurrentUser, request: Request
) -> GenerationOut:
    # Interviews come only through companies (/internal/generations), which checks membership.
    if body.kind == GenerationKind.INTERVIEW:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Interviews are created from a company")

    await hit(
        get_redis(),
        f"rate:generations:{user.uid}",
        settings.generation_limit,
        settings.generation_window_seconds,
    )
    # Credits first: a refused attempt mustn't use up the day's cap for everyone.
    generation_id = uuid4()
    await billing.hold_kit(user.uid, generation_id)

    try:
        await use_daily_budget()
    except HTTPException:
        await billing.release_kit(generation_id)
        raise

    try:
        generation = await generations.create(
            user.uid, body.text, body.kind, body.company_id, user.language, generation_id
        )
    except Exception:
        await billing.release_kit(generation_id)
        raise
    await tasks.enqueue(RUN_GENERATION, {"generation_id": str(generation.id)})
    await track("kit_started", user_id=user.uid, kind=body.kind, language=user.language)

    return GenerationOut.model_validate(generation)


@router.get("")
async def list_unfinished(user: CurrentUser, page: PageParams) -> list[GenerationSummary]:
    """Preparations still generating, waiting for topic review, or failed, newest first."""
    rows = await generations.list_unfinished(user.uid, page.offset, page.limit)

    return [GenerationSummary.of(item) for item in rows]


@router.get("/{generation_id}")
async def get_generation(generation_id: UUID, user: CurrentUser) -> GenerationOut:
    return GenerationOut.model_validate(await get_owned(generation_id, user))


@router.post("/{generation_id}/review")
async def review_generation(
    generation_id: UUID, body: ReviewRequest, user: CurrentUser, request: Request
) -> GenerationOut:
    generation = await get_owned(generation_id, user)

    return GenerationOut.model_validate(await submit_review(generation, body))


@router.post("/{generation_id}/retry")
async def retry(generation_id: UUID, user: CurrentUser, request: Request) -> GenerationOut:
    generation = await get_owned(generation_id, user)

    return GenerationOut.model_validate(await retry_generation(generation))


@router.post("/{generation_id}/cancel")
async def cancel(generation_id: UUID, user: CurrentUser) -> GenerationOut:
    """Interviews are cancelled through companies, which also removes the interview."""
    generation = await get_owned(generation_id, user)

    if generation.kind == GenerationKind.INTERVIEW:
        raise HTTPException(status.HTTP_409_CONFLICT, "Interview generations can't be cancelled")

    return GenerationOut.model_validate(await cancel_generation(generation))
