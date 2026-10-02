from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.helpers.review import build_review
from app.helpers.sessions import session_out
from app.schemas.sessions import InviteScoresIn, ScorecardSession, SessionOut, SessionsCreate
from app.service_auth import ServiceCaller
from app.storage import rounds, sessions

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_sessions(body: SessionsCreate, caller: ServiceCaller) -> list[SessionOut]:
    """Creates one session per topic for a candidate invite; returns existing ones if any."""
    existing = await sessions.list_for_invite(body.candidate_invite_id)

    if existing:
        return [session_out(row) for row in existing]

    deadline = (
        datetime.now(UTC) + timedelta(minutes=body.time_limit_minutes)
        if body.time_limit_minutes
        else None
    )
    rows = await sessions.create_many(
        body.user_id, body.candidate_invite_id, body.share_results, body.topics, deadline
    )

    return [session_out(row) for row in rows]


@router.post("/invite-scores")
async def invite_scores(
    body: InviteScoresIn, caller: ServiceCaller
) -> dict[str, dict[str, int | None]]:
    await sessions.finish_expired(body.invite_ids)
    found = await sessions.scores_for_invites(body.invite_ids)

    return {
        str(invite_id): {"progress": progress, "grade": grade, "finished": finished}
        for invite_id, (progress, grade, finished) in found.items()
    }


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
    await sessions.finish_expired([invite_id])
    rows = await sessions.list_for_invite(invite_id)

    if not rows:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No sessions for this invite")

    return [
        ScorecardSession(
            id=row.id,
            topic_title=row.topic_title,
            status=row.status,
            final_score=row.final_score,
            review=build_review(row),
        )
        for row in rows
    ]
