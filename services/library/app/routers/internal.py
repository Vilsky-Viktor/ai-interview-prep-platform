from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.preparations import (
    CreatedOut,
    PreparationIn,
    QuestionOut,
    QuestionText,
    TitleIn,
    TopicOut,
    TopicQuestionsOut,
)
from app.schemas.feedback import ReportOut
from app.schemas.regenerate import QuestionContext, QuestionReplace
from app.schemas.sets import SetContent, SetOut, SetTopicOut
from app.service_auth import ServiceCaller
from app.services.access import require_member
from app.services.questions import question_texts
from app.storage import feedback, preparations

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/preparations", status_code=status.HTTP_201_CREATED)
async def create_preparation(body: PreparationIn, caller: ServiceCaller) -> CreatedOut:
    return CreatedOut(id=await preparations.create(body))


@router.post("/interviews", status_code=status.HTTP_201_CREATED)
async def create_interview(body: PreparationIn, caller: ServiceCaller) -> CreatedOut:
    return CreatedOut(id=await preparations.create_interview(body))


@router.patch("/sets/{set_id}/title", status_code=status.HTTP_204_NO_CONTENT)
async def rename_set(set_id: UUID, body: TitleIn, caller: ServiceCaller) -> None:
    if await preparations.get(set_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Set not found")

    await preparations.set_title(set_id, body.title)


@router.get("/sets/{set_id}")
async def get_set(set_id: UUID, caller: ServiceCaller) -> SetOut:
    question_set = await preparations.get(set_id)

    if question_set is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Set not found")

    topics = await preparations.get_topics(set_id)

    return SetOut(
        id=question_set.id,
        kind=question_set.kind,
        owner_id=question_set.owner_id,
        title=question_set.title,
        level=question_set.level,
        topics=[
            TopicOut(
                id=topic.id,
                title=topic.title,
                subtopics=topic.subtopics,
                question_count=question_count,
            )
            for topic, question_count in topics
        ],
    )


@router.get("/sets/{set_id}/content")
async def get_set_content(set_id: UUID, caller: ServiceCaller) -> SetContent:
    question_set = await preparations.get_content(set_id)

    if question_set is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Set not found")

    return SetContent(
        id=question_set.id,
        title=question_set.title,
        topics=[
            SetTopicOut(
                id=topic.id,
                title=topic.title,
                questions=[
                    QuestionOut(
                        id=question.id,
                        text=question.text,
                        reference_answer=question.reference_answer,
                        options=question.options,
                    )
                    for question in topic.questions
                ],
            )
            for topic in question_set.topics
        ],
    )


@router.get("/sets/{set_id}/question-texts")
async def list_question_texts(set_id: UUID, caller: ServiceCaller) -> dict[str, str]:
    """Current text per question id, so callers can tell a re-generated question apart."""
    if await preparations.get(set_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Set not found")

    return {str(question_id): text for question_id, text in await preparations.question_texts(set_id)}


@router.get("/sets/{set_id}/topics/{topic_id}/questions")
async def list_topic_questions(
    set_id: UUID, topic_id: UUID, caller: ServiceCaller
) -> list[QuestionText]:
    """Question text and feedback counts of one topic in a set, without answers."""
    found = await preparations.get_topic_with_questions(topic_id)

    if found is None or found[0].id != set_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topic not found")

    return await question_texts(found[1].questions)


@router.get("/sets/{set_id}/questions/{question_id}/reports")
async def list_question_reports(
    set_id: UUID, question_id: UUID, caller: ServiceCaller
) -> list[ReportOut]:
    question_set = await preparations.get_for_question(question_id)

    if question_set is None or question_set.id != set_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found")

    reports = await feedback.list_reports(question_id)

    return [ReportOut.model_validate(report, from_attributes=True) for report in reports]


@router.get("/questions/{question_id}/context")
async def get_question_context(question_id: UUID, caller: ServiceCaller) -> QuestionContext:
    found = await preparations.get_question_context(question_id)

    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found")

    question_set, topic = found

    return QuestionContext(
        set_id=question_set.id,
        kind=question_set.kind,
        owner_id=question_set.owner_id,
        level=question_set.level,
        topic=topic.title,
        subtopics=topic.subtopics,
        existing=[question.text for question in topic.questions],
    )


@router.put("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def replace_question(question_id: UUID, body: QuestionReplace, caller: ServiceCaller) -> None:
    await preparations.replace_question(
        question_id,
        body.text,
        body.reference_answer,
        [option.model_dump() for option in body.options],
    )


@router.get("/topics/{topic_id}")
async def get_topic_questions(
    topic_id: UUID, user_id: str, caller: ServiceCaller
) -> TopicQuestionsOut:
    """Questions of a topic the user owns or joined, for starting a round."""
    found = await preparations.get_topic_with_questions(topic_id)

    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topic not found")

    question_set, topic = found
    await require_member(question_set, user_id)

    return TopicQuestionsOut(
        id=topic.id,
        preparation_id=question_set.id,
        title=topic.title,
        question_limit=topic.question_limit,
        questions=[
            QuestionOut(
                id=question.id,
                text=question.text,
                reference_answer=question.reference_answer,
                options=question.options,
            )
            for question in topic.questions
        ],
    )
