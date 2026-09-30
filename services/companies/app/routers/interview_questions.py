from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.auth import CurrentUser
from app.integrations import generation as generation_api
from app.integrations import library
from app.models.interviews import Interview
from app.schemas.interviews import QuestionText, ReportOut, TopicLimitIn
from app.services.access import require_company, require_manager
from app.storage import interviews

router = APIRouter(prefix="/interviews", tags=["interviews"])


async def generated_interview(interview_id: UUID) -> Interview:
    interview = await interviews.get(interview_id)

    if interview is None or interview.set_id is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    return interview


@router.get("/{interview_id}/topics/{topic_id}/questions")
async def list_topic_questions(
    interview_id: UUID, topic_id: UUID, user: CurrentUser
) -> list[QuestionText]:
    interview = await generated_interview(interview_id)
    await require_company(user, interview.company_id)
    questions = await library.get_topic_questions(interview.set_id, topic_id)

    if questions is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topic not found")

    return [QuestionText(**question) for question in questions]


@router.put("/{interview_id}/topics/{topic_id}/limit", status_code=status.HTTP_204_NO_CONTENT)
async def set_topic_limit(
    interview_id: UUID, topic_id: UUID, body: TopicLimitIn, user: CurrentUser
) -> None:
    interview = await generated_interview(interview_id)
    await require_manager(user, interview)
    found = await library.get_set(interview.set_id) or {}
    topic = next(
        (item for item in found.get("topics", []) if str(item["id"]) == str(topic_id)), None
    )

    if topic is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topic not found")

    if body.limit is not None and body.limit > topic["question_count"]:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            f"The topic has only {topic['question_count']} questions",
        )

    await interviews.set_topic_limit(interview.id, topic_id, body.limit)


@router.post("/{interview_id}/questions/{question_id}/regenerate")
async def regenerate_question(interview_id: UUID, question_id: UUID, user: CurrentUser) -> dict:
    interview = await generated_interview(interview_id)
    await require_manager(user, interview)
    response = await generation_api.regenerate_question(question_id, interview.set_id, user.uid)

    if response.is_error:
        raise HTTPException(response.status_code, response.json().get("detail"))

    return response.json()


@router.get("/{interview_id}/questions/{question_id}/reports")
async def list_question_reports(
    interview_id: UUID, question_id: UUID, user: CurrentUser
) -> list[ReportOut]:
    interview = await generated_interview(interview_id)
    await require_manager(user, interview)
    reports = await library.get_question_reports(interview.set_id, question_id)

    if reports is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found")

    return [ReportOut(**report) for report in reports]
