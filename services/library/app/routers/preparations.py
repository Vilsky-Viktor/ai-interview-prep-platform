from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser, OptionalUser
from prepza_common.paging import PageParams

from app.helpers.preparations import summary_out
from app.integrations import rounds
from app.schemas.preparations import (
    MyPreparation,
    PreparationDetail,
    QuestionText,
    TitleIn,
    TopicOut,
    VisibilityIn,
)
from app.services.access import access_for, require_owner
from app.services.questions import question_texts
from app.storage import feedback, preparations

router = APIRouter(prefix="/preparations", tags=["preparations"])


@router.get("")
async def list_mine(user: CurrentUser, page: PageParams) -> list[MyPreparation]:
    """The user's own and joined preparations together, newest first, a page at a time."""
    rows = await preparations.list_mine(user.uid, page.offset, page.limit)

    return [
        MyPreparation(**summary_out(row).model_dump(), owned=row[0].owner_id == user.uid)
        for row in rows
    ]


@router.get("/topics/{topic_id}/questions")
async def list_topic_questions(topic_id: UUID, user: OptionalUser) -> list[QuestionText]:
    """Question text for a topic the viewer can already open."""
    found = await preparations.get_topic_with_question_texts(topic_id)
    question_set, topic = found if found else (None, None)
    user_id = user.uid if user else None
    access = await access_for(question_set, user_id) if question_set else None

    if access is None or topic is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topic not found")

    return await question_texts(topic.questions)


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


@router.delete("/{preparation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preparation(preparation_id: UUID, user: CurrentUser) -> None:
    """Only the owner deletes a preparation; everyone who joined it loses access too.

    Practice data goes first, so a failure there leaves the preparation in place to retry.
    """
    require_owner(await preparations.get(preparation_id), user.uid)
    await rounds.delete_preparation_data(preparation_id)
    await preparations.remove(preparation_id)
