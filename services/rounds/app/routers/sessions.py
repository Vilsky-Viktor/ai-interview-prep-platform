from uuid import UUID

from fastapi import APIRouter
from prepza_common.auth import CurrentUser

from app.helpers.review import build_review
from app.helpers.scores import final_score
from app.helpers.sessions import next_session_question, session_out_titled, topic_out
from app.schemas.review import ReviewItem
from app.schemas.rounds import AnswerCreate, NextQuestion
from app.schemas.sessions import SessionAnswerResult, SessionOut, SessionTopicOut
from app.services.session_access import get_owned_session
from app.services.session_answers import submit_session_answer
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
    return next_session_question(await get_owned_session(session_id, user))


@router.post("/{session_id}/answers", status_code=201)
async def answer_question(
    session_id: UUID, body: AnswerCreate, user: CurrentUser
) -> SessionAnswerResult:
    return await submit_session_answer(await get_owned_session(session_id, user), body)


@router.get("/{session_id}/review")
async def review_session(session_id: UUID, user: CurrentUser) -> list[ReviewItem]:
    """Candidates see whether they were right only when share_results is on; never the key."""
    row = await get_owned_session(session_id, user)
    items = build_review(row)

    for item in items:
        item.correct_option_index = None

        if item.answer and not row.share_results:
            item.answer.correct = None

    return items


@router.post("/{session_id}/finish")
async def finish(session_id: UUID, user: CurrentUser) -> SessionOut:
    row = await get_owned_session(session_id, user)
    final = final_score([answer.score for answer in row.answers], len(row.questions))
    await sessions.finish(row.id, final)

    return await session_out_titled(await sessions.get(session_id))
