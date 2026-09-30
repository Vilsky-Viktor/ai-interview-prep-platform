from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status

from app.auth import CurrentUser
from app.config.settings import settings
from app.constants.kinds import GenerationKind
from app.helpers.rate_limit import hit
from app.integrations import library
from app.schemas.regenerate import RegeneratedOut
from app.services.regenerate import regenerate

router = APIRouter(prefix="/questions", tags=["questions"])


@router.post("/{question_id}/regenerate")
async def regenerate_question(
    question_id: UUID, user: CurrentUser, request: Request
) -> RegeneratedOut:
    """Only the owner of a preparation can replace its questions."""
    context = await library.get_question_context(question_id)

    if (
        context is None
        or context.kind != GenerationKind.PREPARATION
        or context.owner_id != user.uid
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found")

    await hit(
        request.app.state.arq,
        f"rate:regenerations:{user.uid}",
        settings.regeneration_limit,
        settings.generation_window_seconds,
    )
    question = await regenerate(question_id, context)

    if question is None:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Couldn't generate a new question")

    return question
