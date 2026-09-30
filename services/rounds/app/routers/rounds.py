from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status

from app.auth import CurrentUser
from app.helpers.coverage import current_scores, topic_texts
from app.helpers.review import build_review
from app.helpers.rounds import next_question, round_out
from app.integrations import library
from app.schemas.review import ReviewItem
from app.schemas.rounds import AnswerCreate, AnswerResult, NextQuestion, RoundCreate, RoundOut
from app.services.access import get_owned_round
from app.services.answers import submit_answer
from app.services.finish import finish_round
from app.storage import progress, rounds

router = APIRouter(prefix="/rounds", tags=["rounds"])


@router.post("")
async def create_round(body: RoundCreate, user: CurrentUser, response: Response) -> RoundOut:
    topic = await library.get_topic_questions(body.topic_id, user.uid)

    if topic is None or not topic.questions:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topic not found")

    existing = await rounds.get_in_progress(user.uid, body.topic_id, body.mode)

    if existing:
        return round_out(existing)

    rows = await progress.for_topic(user.uid, topic.id, body.mode)
    latest = current_scores(rows, topic_texts(topic))
    response.status_code = status.HTTP_201_CREATED

    return round_out(await rounds.create(user.uid, topic, body.mode, latest))


@router.get("/{round_id}")
async def get_round(round_id: UUID, user: CurrentUser) -> RoundOut:
    return round_out(await get_owned_round(round_id, user))


@router.get("/{round_id}/next")
async def get_next_question(round_id: UUID, user: CurrentUser) -> NextQuestion | None:
    """The next unanswered question, or null when every question is answered."""
    return next_question(await get_owned_round(round_id, user))


@router.post("/{round_id}/answers", status_code=status.HTTP_201_CREATED)
async def answer_question(round_id: UUID, body: AnswerCreate, user: CurrentUser) -> AnswerResult:
    return await submit_answer(await get_owned_round(round_id, user), body)


@router.get("/{round_id}/review")
async def review_round(round_id: UUID, user: CurrentUser) -> list[ReviewItem]:
    return build_review(await get_owned_round(round_id, user))


@router.post("/{round_id}/finish")
async def finish(round_id: UUID, user: CurrentUser) -> RoundOut:
    await finish_round(await get_owned_round(round_id, user), user)

    return round_out(await rounds.get(round_id))


@router.delete("/{round_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_round(round_id: UUID, user: CurrentUser) -> None:
    question_ids = await rounds.remove(round_id, user.uid)

    if question_ids is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Round not found")

    # Its answers no longer count towards coverage.
    await progress.rebuild(user.uid, question_ids)
