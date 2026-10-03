from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.constants.integrity import IntegritySignal
from app.helpers.review import add_signals, build_review
from app.helpers.sessions import session_out
from app.schemas.sessions import (
    InviteScoresIn,
    MasteredCountsIn,
    ScorecardSession,
    SessionOut,
    SessionsCreate,
)
from app.service_auth import ServiceCaller
from app.storage import certificates, rounds, sessions

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_sessions(body: SessionsCreate, caller: ServiceCaller) -> list[SessionOut]:
    """Creates one session per topic for a candidate invite; returns existing ones if any."""
    existing = await sessions.list_for_invite(body.candidate_invite_id)

    if existing:
        return [session_out(row) for row in existing]

    rows = await sessions.create_many(
        body.user_id,
        body.candidate_invite_id,
        body.topics,
        body.question_seconds,
    )

    return [session_out(row) for row in rows]


@router.post("/invite-scores")
async def invite_scores(
    body: InviteScoresIn, caller: ServiceCaller
) -> dict[str, dict[str, int | None]]:
    found = await sessions.scores_for_invites(body.invite_ids)

    return {
        str(invite_id): {"progress": progress, "grade": grade, "finished": finished}
        for invite_id, (progress, grade, finished) in found.items()
    }


@router.post("/mastered-counts")
async def mastered_counts(body: MasteredCountsIn, caller: ServiceCaller) -> dict[str, int]:
    """Topics with a certificate per preparation, so library can tell which ones are done."""
    found = await certificates.mastered_counts(body.user_id, body.preparation_ids)

    return {str(preparation_id): count for preparation_id, count in found.items()}


@router.delete("/preparations/{preparation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preparation_data(preparation_id: UUID, caller: ServiceCaller) -> None:
    """Called by library before it deletes a preparation; safe to repeat."""
    await rounds.remove_for_preparation(preparation_id)


@router.delete("/interviews/{interview_set_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview_data(interview_set_id: UUID, caller: ServiceCaller) -> None:
    """Called by companies before it deletes an interview; safe to repeat."""
    await sessions.remove_for_interview(interview_set_id)


@router.get("/invites/{invite_id}/scorecard")
async def invite_scorecard(invite_id: UUID, caller: ServiceCaller) -> list[ScorecardSession]:
    rows = await sessions.list_for_invite(invite_id)

    if not rows:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No sessions for this invite")

    cards = []

    for row in rows:
        review = build_review(row)
        add_signals(review, row.signals)
        kinds = [signal.kind for signal in row.signals]
        cards.append(
            ScorecardSession(
                id=row.id,
                topic_title=row.topic_title,
                status=row.status,
                final_score=row.final_score,
                tab_leaves=kinds.count(IntegritySignal.TAB_LEAVE),
                copies=kinds.count(IntegritySignal.COPY),
                fast_answers=sum(item.answer is not None and item.answer.fast for item in review),
                review=review,
            )
        )

    return cards
