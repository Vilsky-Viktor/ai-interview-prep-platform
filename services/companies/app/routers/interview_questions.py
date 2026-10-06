from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser
from prepza_common.paging import PageParams

from app.integrations import generation as generation_api
from app.integrations import library
from app.models.interviews import Interview
from app.schemas.interviews import QuestionText, ReportOut, TopicLimitIn
from app.services.access import require_company, require_editor
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
    await require_editor(user, interview.company_id)
    found = await library.get_set(interview.set_id) or {}
    topic = next(
        (item for item in found.get("topics", []) if str(item["id"]) == str(topic_id)), None
    )

    if topic is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topic not found")

    if body.limit > topic["question_count"]:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            f"The topic has only {topic['question_count']} questions",
        )

    await interviews.set_topic_limit(interview.id, topic_id, body.limit)


@router.post("/{interview_id}/questions/{question_id}/regenerate")
async def regenerate_question(interview_id: UUID, question_id: UUID, user: CurrentUser) -> dict:
    interview = await generated_interview(interview_id)
    await require_editor(user, interview.company_id)
    response = await generation_api.regenerate_question(question_id, interview.set_id, user.uid)

    if response.is_error:
        raise HTTPException(response.status_code, response.json().get("detail"))

    return response.json()


@router.post(
    "/{interview_id}/questions/{question_id}/wrong", status_code=status.HTTP_204_NO_CONTENT
)
async def mark_wrong(interview_id: UUID, question_id: UUID, user: CurrentUser) -> None:
    """One click: the marked answer is wrong. The verifier checks it and fixes or replaces it."""
    interview = await generated_interview(interview_id)
    await require_editor(user, interview.company_id)
    context = await library.get_question_context(question_id)

    if context is None or str(context["set_id"]) != str(interview.set_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found")

    await library.mark_wrong(question_id)


@router.get("/{interview_id}/questions/{question_id}/reports")
async def list_question_reports(
    interview_id: UUID, question_id: UUID, user: CurrentUser, page: PageParams
) -> list[ReportOut]:
    """Candidates' reports on a question, read where it's fixed: owners and admins."""
    interview = await generated_interview(interview_id)
    await require_editor(user, interview.company_id)
    reports = await library.get_question_reports(interview.set_id, question_id, page)

    if reports is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found")

    return [ReportOut(**report) for report in reports]
