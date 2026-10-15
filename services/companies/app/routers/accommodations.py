from uuid import UUID

from fastapi import APIRouter
from prepza_common.auth import CurrentUser

from app.schemas.invites import ExtraTimeIn
from app.service_auth import Via
from app.services import candidate_changes
from app.services.interview_access import candidate_for

# Accommodations for candidates who need them: extra time on each question.
router = APIRouter(prefix="/interviews", tags=["candidates"])


@router.put("/{interview_id}/candidates/{invite_id}/extra-time", status_code=204)
async def set_extra_time(
    interview_id: UUID, invite_id: UUID, body: ExtraTimeIn, user: CurrentUser, via: Via
) -> None:
    interview, invite, _, _ = await candidate_for(user, interview_id, invite_id, editor=True)
    await candidate_changes.set_extra_time(interview, invite, body.extra_time, user.uid, via)
