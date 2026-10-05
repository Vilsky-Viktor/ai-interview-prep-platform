from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from prepza_common.rate_limit import hit
from prepza_common.superadmin import SuperadminUser

from app.config.settings import settings
from app.constants.generation import RUN_GENERATION
from app.constants.kinds import GenerationKind
from app.helpers.language import text_language
from app.integrations import library, tasks
from app.integrations.redis import get_redis
from app.models.generation import Generation
from app.schemas.generation import GenerationOut, ReviewRequest, TemplateGenerationCreate
from app.schemas.regenerate import RegeneratedOut
from app.services.budget import use_daily_budget
from app.services.cancel import cancel_generation
from app.services.regenerate import regenerate
from app.services.retry import retry_generation
from app.services.review import submit_review
from app.storage import generations

# The superadmin's templates (docs/company-plan.md, Phase 2): the same pipeline as a company's test,
# saved without a company. Everyone else gets "not found".
router = APIRouter(prefix="/superadmin", tags=["superadmin"])


async def get_template_generation(generation_id: UUID) -> Generation:
    generation = await generations.get(generation_id)

    if generation is None or generation.kind != GenerationKind.TEMPLATE:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Generation not found")

    return generation


@router.post("/templates", status_code=status.HTTP_201_CREATED)
async def create_template(
    body: TemplateGenerationCreate, superadmin: SuperadminUser
) -> GenerationOut:
    await use_daily_budget()
    generation = await generations.create(
        superadmin.uid,
        body.text,
        language=body.generate_in or text_language(body.text, superadmin.language),
        kind=GenerationKind.TEMPLATE,
    )
    await tasks.enqueue(RUN_GENERATION, {"generation_id": str(generation.id)})

    return GenerationOut.model_validate(generation)


@router.get("/generations/{generation_id}")
async def get_generation(generation_id: UUID, superadmin: SuperadminUser) -> GenerationOut:
    return GenerationOut.model_validate(await get_template_generation(generation_id))


@router.post("/generations/{generation_id}/review")
async def review_generation(
    generation_id: UUID, body: ReviewRequest, superadmin: SuperadminUser
) -> GenerationOut:
    generation = await get_template_generation(generation_id)

    return GenerationOut.model_validate(await submit_review(generation, body))


@router.post("/generations/{generation_id}/retry")
async def retry(generation_id: UUID, superadmin: SuperadminUser) -> GenerationOut:
    generation = await get_template_generation(generation_id)

    return GenerationOut.model_validate(await retry_generation(generation))


@router.post("/generations/{generation_id}/cancel")
async def cancel(generation_id: UUID, superadmin: SuperadminUser) -> GenerationOut:
    generation = await get_template_generation(generation_id)

    return GenerationOut.model_validate(await cancel_generation(generation))


@router.post("/templates/{template_id}/questions/{question_id}/regenerate")
async def regenerate_question(
    template_id: UUID, question_id: UUID, superadmin: SuperadminUser
) -> RegeneratedOut:
    context = await library.get_question_context(question_id)

    if context is None or context.set_id != template_id or context.kind != "template":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found")

    await hit(
        get_redis(),
        f"rate:regenerations:{superadmin.uid}",
        settings.regeneration_limit,
        settings.generation_window_seconds,
    )
    question = await regenerate(question_id, context)

    if question is None:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Couldn't generate a new question")

    return question
