from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from prepza_common.rate_limit import hit

from app.config.settings import settings
from app.constants.generation import RUN_GENERATION, VERIFY_QUESTION
from app.helpers.language import text_language
from app.integrations import library, tasks
from app.integrations.redis import get_redis
from app.models.generation import Generation
from app.schemas.generation import GenerationOut, InterviewGenerationCreate, ReviewRequest
from app.schemas.regenerate import RegeneratedOut, RegenerateIn
from app.schemas.verify import VerifyIn
from app.service_auth import ServiceCaller
from app.services.budget import use_daily_budget
from app.services.cancel import cancel_generation
from app.services.regenerate import regenerate
from app.services.retry import retry_generation
from app.services.review import submit_review
from app.storage import generations

router = APIRouter(prefix="/internal", tags=["internal"])


async def get_company_generation(generation_id: UUID, company_id: UUID) -> Generation:
    generation = await generations.get(generation_id)

    if generation is None or generation.company_id != company_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Generation not found")

    return generation


@router.post("/generations", status_code=status.HTTP_201_CREATED)
async def create_interview_generation(
    body: InterviewGenerationCreate, caller: ServiceCaller, request: Request
) -> GenerationOut:
    """A company's test; companies charges per candidate, so generating it is free."""
    await hit(
        get_redis(),
        f"rate:generations:{body.owner_uid}",
        settings.generation_limit,
        settings.generation_window_seconds,
    )
    await use_daily_budget()
    generation = await generations.create(
        body.owner_uid,
        body.text,
        body.company_id,
        body.generate_in or text_language(body.text, body.language),
    )
    await tasks.enqueue(RUN_GENERATION, {"generation_id": str(generation.id)})

    return GenerationOut.model_validate(generation)


@router.get("/generations/{generation_id}")
async def get_interview_generation(
    generation_id: UUID, company_id: UUID, caller: ServiceCaller
) -> GenerationOut:
    """For a caller that already checked the user belongs to the company."""
    return GenerationOut.model_validate(await get_company_generation(generation_id, company_id))


@router.post("/generations/{generation_id}/review")
async def review_interview_generation(
    generation_id: UUID,
    company_id: UUID,
    body: ReviewRequest,
    caller: ServiceCaller,
    request: Request,
) -> GenerationOut:
    """For a caller that already checked the user may manage the company's interviews."""
    generation = await get_company_generation(generation_id, company_id)

    return GenerationOut.model_validate(await submit_review(generation, body))


@router.post("/generations/{generation_id}/retry")
async def retry_interview_generation(
    generation_id: UUID, company_id: UUID, caller: ServiceCaller, request: Request
) -> GenerationOut:
    """For a caller that already checked the user may manage the company's interviews."""
    generation = await get_company_generation(generation_id, company_id)

    return GenerationOut.model_validate(await retry_generation(generation))


@router.post("/generations/{generation_id}/cancel")
async def cancel_interview_generation(
    generation_id: UUID, company_id: UUID, caller: ServiceCaller
) -> GenerationOut:
    """For a caller that already checked the user may manage the company's interviews."""
    generation = await get_company_generation(generation_id, company_id)

    return GenerationOut.model_validate(await cancel_generation(generation))


@router.post("/questions/{question_id}/regenerate")
async def regenerate_interview_question(
    question_id: UUID, body: RegenerateIn, caller: ServiceCaller, request: Request
) -> RegeneratedOut:
    """For a caller that already checked the user may edit this set."""
    context = await library.get_question_context(question_id)

    if context is None or context.set_id != body.set_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found")

    await hit(
        get_redis(),
        f"rate:regenerations:{body.user_id}",
        settings.regeneration_limit,
        settings.generation_window_seconds,
    )
    question = await regenerate(question_id, context)

    if question is None:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Couldn't generate a new question")

    return question


@router.post("/questions/{question_id}/verify", status_code=status.HTTP_202_ACCEPTED)
async def verify_question(
    question_id: UUID, body: VerifyIn, caller: ServiceCaller, request: Request
) -> None:
    """The library flagged the question; the worker checks it and fixes or replaces it."""
    await tasks.enqueue(
        VERIFY_QUESTION, {"question_id": str(question_id), "flag": body.flag, "now": body.now}
    )
