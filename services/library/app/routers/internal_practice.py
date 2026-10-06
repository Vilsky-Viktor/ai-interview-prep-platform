from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.constants.sets import SetKind, Stage
from app.schemas.preparations import QuestionOut
from app.schemas.sets import SetContent, SetTopicOut
from app.service_auth import ServiceCaller
from app.storage import preparations

# Free practice for talents: only a template's revealed questions, never its private ones.
router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/templates/{template_id}/practice")
async def practice_content(template_id: UUID, caller: ServiceCaller) -> SetContent:
    """The template's revealed questions, with answers, by topic; topics without any are left
    out. Rounds picks each practice round's questions from them."""
    template = await preparations.get_content(template_id)

    if template is None or template.kind != SetKind.TEMPLATE:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Template not found")

    topics = [
        SetTopicOut(
            id=topic.id,
            title=topic.title,
            questions=[
                QuestionOut(id=question.id, text=question.text, options=question.options)
                for question in topic.questions
                if question.stage == Stage.REVEALED
            ],
        )
        for topic in template.topics
    ]

    return SetContent(
        id=template.id,
        title=template.title,
        topics=[topic for topic in topics if topic.questions],
    )
