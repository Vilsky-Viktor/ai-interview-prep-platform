from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status

from app.auth import CurrentUser
from app.config.settings import settings
from app.helpers.rate_limit import hit
from app.models.generation import Generation
from app.schemas.generation import GenerationCreate, GenerationOut, ReviewRequest
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
    await hit(
        request.app.state.arq,
        f"rate:generations:{user.uid}",
        settings.generation_limit,
        settings.generation_window_seconds,
    )

    generation = await generations.create(user.uid, body.text, body.kind, body.company_id)
    await request.app.state.arq.enqueue_job("run_generation", str(generation.id))

    return GenerationOut.model_validate(generation)


@router.get("/{generation_id}")
async def get_generation(generation_id: UUID, user: CurrentUser) -> GenerationOut:
    return GenerationOut.model_validate(await get_owned(generation_id, user))


@router.post("/{generation_id}/review")
async def review_generation(
    generation_id: UUID, body: ReviewRequest, user: CurrentUser, request: Request
) -> GenerationOut:
    generation = await get_owned(generation_id, user)

    return GenerationOut.model_validate(
        await submit_review(request.app.state.arq, generation, body)
    )


@router.post("/{generation_id}/retry")
async def retry(generation_id: UUID, user: CurrentUser, request: Request) -> GenerationOut:
    generation = await get_owned(generation_id, user)

    return GenerationOut.model_validate(
        await retry_generation(request.app.state.arq, generation)
    )
