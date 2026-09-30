import random

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


async def interview_out(interview: Interview) -> InterviewOut:
    interview = await attach_set(interview)
    title = None

    if interview.set_id:
        found = await library.get_set(interview.set_id)
        title = found["title"] if found else None

    return InterviewOut(
        id=interview.id,
        generation_id=interview.generation_id,
        set_id=interview.set_id,
        title=title,
        mode=interview.mode,
        share_results=interview.share_results,
        candidate_count=len(interview.invites),
        created_at=interview.created_at,
    )


def topics_out(found: dict, limits: dict[str, int]) -> list[TopicOut]:
    return [
        TopicOut(
            id=topic["id"],
            title=topic["title"],
            subtopics=topic.get("subtopics", []),
            question_count=topic["question_count"],
            question_limit=limits.get(str(topic["id"])),
        )
        for topic in found.get("topics", [])
    ]


def pick_questions(questions: list, limit: int | None) -> list:
    """Each candidate gets a fresh random subset when the topic is limited."""
    if limit is None or limit >= len(questions):
        return questions

    return random.sample(questions, limit)
