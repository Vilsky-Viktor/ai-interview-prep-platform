from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser
from prepza_common.rate_limit import hit

from app.constants.integrity import SIGNALS_PER_MINUTE, SIGNALS_WINDOW_SECONDS
from app.constants.rounds import SECTION_IN_PROGRESS, TIME_GRACE_SECONDS, RoundStatus
from app.helpers.review import build_review
from app.helpers.sessions import (
    next_session_question,
    seconds_left,
    topic_out,
)
from app.integrations.redis import get_redis
from app.schemas.review import ReviewItem
from app.schemas.rounds import AnswerCreate, NextQuestion
from app.schemas.sessions import SessionAnswerResult, SessionOut, SessionTopicOut, SignalIn
from app.services import outbox as outbox_service
from app.services.session_access import get_owned_session
from app.services.session_answers import submit_session_answer
from app.services.session_titles import session_out_titled
from app.storage import sessions

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/{session_id}")
async def get_session(session_id: UUID, user: CurrentUser) -> SessionOut:
    return await session_out_titled(await get_owned_session(session_id, user))


@router.get("/{session_id}/topics")
async def list_topics(session_id: UUID, user: CurrentUser) -> list[SessionTopicOut]:
    """Every topic of this candidate's interview, so they can open the ones besides the first."""
    row = await get_owned_session(session_id, user)
    rows = await sessions.list_for_invite(row.candidate_invite_id)

    return [topic_out(item) for item in rows if item.user_id == user.uid]


@router.get("/{session_id}/next")
async def get_next_question(session_id: UUID, user: CurrentUser) -> NextQuestion | None:
    row = await get_owned_session(session_id, user)

    # A finished section shows nothing more: its unanswered questions stay unseen.
    if row.status != RoundStatus.IN_PROGRESS:
        return None

    question = next_session_question(row)

    if question is None:
        return None

    if row.question_shown_at is None:
        row.question_shown_at = await sessions.mark_shown(row.id)

    question.seconds_left = seconds_left(row, datetime.now(UTC))

    return question


@router.post("/{session_id}/signals", status_code=204)
async def add_signal(session_id: UUID, body: SignalIn, user: CurrentUser) -> None:
    """The candidate's browser reports leaving the page or copying, saved with the question on
    screen so the scorecard can show where it happened."""
    row = await get_owned_session(session_id, user)

    if row.status != RoundStatus.IN_PROGRESS:
        return

    await hit(get_redis(), f"rate:signals:{row.id}", SIGNALS_PER_MINUTE, SIGNALS_WINDOW_SECONDS)
    question = next_session_question(row) if row.question_shown_at else None
    await sessions.add_signal(row.id, question.question_id if question else None, body.kind)


@router.post("/{session_id}/answers", status_code=201)
async def answer_question(
    session_id: UUID, body: AnswerCreate, user: CurrentUser
) -> SessionAnswerResult:
    # An answer sent just before the clock ran out still counts.
    row = await get_owned_session(session_id, user, TIME_GRACE_SECONDS)

    return await submit_session_answer(row, body)


@router.get("/{session_id}/review")
async def review_session(session_id: UUID, user: CurrentUser) -> list[ReviewItem]:
    """Once a section is finished, candidates see the questions they answered and their picks,
    never whether they were right or the key. Never while it runs: that would show questions
    before their clock starts."""
    row = await get_owned_session(session_id, user)

    if row.status == RoundStatus.IN_PROGRESS:
        raise HTTPException(status.HTTP_409_CONFLICT, SECTION_IN_PROGRESS)

    items = [item for item in build_review(row) if item.answer]

    for item in items:
        item.correct_option_index = None

        if item.answer:
            item.answer.correct = None

    return items


@router.post("/{session_id}/finish")
async def finish(session_id: UUID, user: CurrentUser) -> SessionOut:
    row = await get_owned_session(session_id, user)
    await sessions.finish(row.id)
    await outbox_service.flush_quietly()

    return await session_out_titled(await sessions.get(session_id))
