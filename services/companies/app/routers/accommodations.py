from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser

from app.schemas.invites import ExtraTimeIn
from app.service_auth import Via
from app.services import candidate_changes
from app.services.access import require_editor
from app.storage import interviews, invites

# Accommodations for candidates who need them: extra time on each question.
router = APIRouter(prefix="/interviews", tags=["candidates"])


@router.put("/{interview_id}/candidates/{invite_id}/extra-time", status_code=204)
async def set_extra_time(
    interview_id: UUID, invite_id: UUID, body: ExtraTimeIn, user: CurrentUser, via: Via
) -> None:
    interview = await interviews.get(interview_id)
    invite = await invites.get(invite_id)

    if interview is None or invite is None or invite.interview_id != interview.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate not found")

    await require_editor(user, interview.company_id)
    await candidate_changes.set_extra_time(interview, invite, body.extra_time, user.uid, via)
