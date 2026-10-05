from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.constants.integrity import IntegritySignal
from app.helpers.review import add_signals, build_review
from app.helpers.sessions import session_out
from app.helpers.talents import suggestions
from app.schemas.sessions import (
    InviteScoresIn,
    ScorecardSession,
    SessionOut,
    SessionsCreate,
)
from app.schemas.talents import SuggestedTalent, SuggestionsIn
from app.service_auth import ServiceCaller
from app.storage import sessions, talents

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
        body.preview,
    )

    return [session_out(row) for row in rows]


@router.post("/invite-scores")
async def invite_scores(
    body: InviteScoresIn, caller: ServiceCaller
) -> dict[str, dict[str, int | None]]:
    found = await sessions.scores_for_invites(body.invite_ids)

    return {str(invite_id): totals for invite_id, totals in found.items()}


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


@router.post("/suggestions")
async def talent_suggestions(body: SuggestionsIn, caller: ServiceCaller) -> list[SuggestedTalent]:
    """For a company's test: talents who agreed to be suggested and did well in their first
    round on one of these templates (the ones for similar roles, closest first)."""
    rows, links = await talents.practice_of_consenting(body.template_ids)

    return suggestions(rows, links, body.template_ids)
