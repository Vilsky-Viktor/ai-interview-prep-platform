import random

from app.constants.interviews import DEFAULT_TOPIC_QUESTIONS, InterviewStatus
from app.integrations import generation as generation_api
from app.integrations import library
from app.models.interviews import Interview
from app.schemas.interviews import InterviewOut, TopicOut
from app.storage import interviews


async def attach_set(interview: Interview) -> Interview:
    if interview.set_id:
        return interview

    row = await generation_api.get(interview.generation_id, interview.company_id)
    set_id = row.get("preparation_id") if row else None

    if set_id:
        await interviews.set_set_id(interview.id, set_id)
        interview.set_id = set_id

    return interview


async def interview_title(interview: Interview) -> str | None:
    """The stored title. Interviews finished before titles were stored fetch it once."""
    if interview.title or not interview.set_id:
        return interview.title

    found = await library.get_set(interview.set_id)

    if found:
        await interviews.set_title(interview.id, found["title"])
        interview.title = found["title"]

    return interview.title


def interview_status(hired: bool, candidate_count: int) -> InterviewStatus:
    if hired:
        return InterviewStatus.HIRED

    return InterviewStatus.IN_PROCESS if candidate_count else InterviewStatus.NEW


async def interview_out(interview: Interview) -> InterviewOut:
    interview = await attach_set(interview)
    title = await interview_title(interview)

    return InterviewOut(
        id=interview.id,
        generation_id=interview.generation_id,
        set_id=interview.set_id,
        title=title,
        question_seconds=interview.question_seconds,
        candidate_count=len(interview.invites),
        hired=interview.hired,
        pass_mark=interview.pass_mark,
        link_token=interview.link_token,
        status=interview_status(interview.hired, len(interview.invites)),
        created_at=interview.created_at,
    )


def topic_limit(limits: dict[str, int], topic_id) -> int:
    """Questions a candidate gets from the topic: the manager's number, or the default."""
    return limits.get(str(topic_id), DEFAULT_TOPIC_QUESTIONS)


def topics_out(found: dict, limits: dict[str, int]) -> list[TopicOut]:
    return [
        TopicOut(
            id=topic["id"],
            title=topic["title"],
            subtopics=topic.get("subtopics", []),
            question_count=topic["question_count"],
            question_limit=min(topic_limit(limits, topic["id"]), topic["question_count"]),
        )
        for topic in found.get("topics", [])
    ]


def pick_questions(questions: list, limit: int) -> list:
    """Each candidate gets a fresh random subset, or every question when the topic has no more."""
    if limit >= len(questions):
        return questions

    return random.sample(questions, limit)


def session_topics(interview: Interview, content: dict) -> list[dict]:
    """Each topic with a fresh random subset of its questions, as rounds starts sessions."""
    return [
        {
            "id": topic["id"],
            "preparation_id": content["id"],
            "title": topic["title"],
            "questions": pick_questions(
                topic["questions"], topic_limit(interview.topic_limits, topic["id"])
            ),
        }
        for topic in content["topics"]
    ]
