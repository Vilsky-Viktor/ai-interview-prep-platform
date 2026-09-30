from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.helpers.review import build_review
from app.helpers.sessions import session_out
from app.schemas.sessions import InviteScoresIn, ScorecardSession, SessionOut, SessionsCreate
from app.service_auth import ServiceCaller
from app.storage import sessions

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_sessions(body: SessionsCreate, caller: ServiceCaller) -> list[SessionOut]:
    """Creates one session per topic for a candidate invite; returns existing ones if any."""
    existing = await sessions.list_for_invite(body.candidate_invite_id)

    if existing:
        return [session_out(row) for row in existing]

    rows = await sessions.create_many(
        body.user_id, body.candidate_invite_id, body.mode, body.share_results, body.topics
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


@router.get("/invites/{invite_id}/scorecard")
async def invite_scorecard(invite_id: UUID, caller: ServiceCaller) -> list[ScorecardSession]:
    rows = await sessions.list_for_invite(invite_id)

    if not rows:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No sessions for this invite")

    return [
        ScorecardSession(
            id=row.id,
            topic_title=row.topic_title,
            mode=row.mode,
            status=row.status,
            final_score=row.final_score,
            review=build_review(row),
        )
        for row in rows
    ]
