from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.auth import CurrentUser, OptionalUser
from app.helpers.preparations import summary_out
from app.schemas.preparations import (
    PreparationDetail,
    PreparationSummary,
    QuestionText,
    TitleIn,
    TopicLimitIn,
    TopicOut,
    VisibilityIn,
)
from app.services.access import access_for, require_owner
from app.services.questions import question_texts
from app.storage import feedback, preparations

router = APIRouter(prefix="/preparations", tags=["preparations"])


@router.get("")
async def list_preparations(user: CurrentUser) -> list[PreparationSummary]:
    return [summary_out(row) for row in await preparations.list_for_owner(user.uid)]


@router.get("/joined")
async def list_joined(user: CurrentUser) -> list[PreparationSummary]:
    return [summary_out(row) for row in await preparations.list_joined(user.uid)]


@router.get("/topics/{topic_id}/questions")
async def list_topic_questions(topic_id: UUID, user: OptionalUser) -> list[QuestionText]:
    """Question text for a topic the viewer can already open."""
    found = await preparations.get_topic_with_questions(topic_id)
    question_set, topic = found if found else (None, None)
    user_id = user.uid if user else None
    access = await access_for(question_set, user_id) if question_set else None

    if access is None or topic is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topic not found")

    return await question_texts(topic.questions)


@router.put("/topics/{topic_id}/limit", status_code=status.HTTP_204_NO_CONTENT)
async def set_topic_limit(topic_id: UUID, body: TopicLimitIn, user: CurrentUser) -> None:
    """Only the owner limits how many of the topic's questions each round asks."""
    found = await preparations.get_topic_with_questions(topic_id)
    question_set, topic = found if found else (None, None)
    require_owner(question_set, user.uid)

    if body.limit is not None and body.limit > len(topic.questions):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            f"The topic has only {len(topic.questions)} questions",
        )

    await preparations.set_topic_limit(topic_id, body.limit)


@router.get("/{preparation_id}")
async def get_preparation(preparation_id: UUID, user: OptionalUser) -> PreparationDetail:
    """Owners and joined users see their preparation; anyone sees a public one."""
    row = await preparations.get_summary(preparation_id)
    user_id = user.uid if user else None
    access = await access_for(row[0], user_id) if row else None

    if access is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Preparation not found")

    topics = await preparations.get_topics(preparation_id)
    my_rating = await feedback.my_preparation_rating(preparation_id, user_id) if user_id else None

    return PreparationDetail(
        **summary_out(row).model_dump(),
        requirements=row[0].requirements,
        topics=[
            TopicOut(
                id=topic.id,
                title=topic.title,
                subtopics=topic.subtopics,
                question_count=question_count,
                question_limit=topic.question_limit,
            )
            for topic, question_count in topics
        ],
        access=access,
        my_rating=my_rating,
    )


@router.patch("/{preparation_id}/title", status_code=status.HTTP_204_NO_CONTENT)
async def update_title(preparation_id: UUID, body: TitleIn, user: CurrentUser) -> None:
    """Only the preparation's owner can rename it."""
    require_owner(await preparations.get(preparation_id), user.uid)
    await preparations.set_title(preparation_id, body.title)


@router.patch("/{preparation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_visibility(preparation_id: UUID, body: VisibilityIn, user: CurrentUser) -> None:
    require_owner(await preparations.get(preparation_id), user.uid)
    await preparations.set_visibility(preparation_id, body.visibility)
