from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser

from app.constants.audit import AuditAction
from app.constants.invites import EXTRA_TIME_STARTED, NOT_STARTED
from app.schemas.invites import ExtraTimeIn
from app.services.access import require_company
from app.storage import audit, interviews, invites

# Accommodations for candidates who need them: extra time on each question.
router = APIRouter(prefix="/interviews", tags=["candidates"])


@router.put("/{interview_id}/candidates/{invite_id}/extra-time", status_code=204)
async def set_extra_time(
    interview_id: UUID, invite_id: UUID, body: ExtraTimeIn, user: CurrentUser
) -> None:
    interview = await interviews.get(interview_id)
    invite = await invites.get(invite_id)

    if interview is None or invite is None or invite.interview_id != interview.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate not found")

    await require_company(user, interview.company_id)

    if invite.status not in NOT_STARTED:
        raise HTTPException(status.HTTP_409_CONFLICT, EXTRA_TIME_STARTED)

    await invites.set_extra_time(invite.id, body.extra_time)
    await audit.record(interview.company_id, user.uid, AuditAction.EXTRA_TIME_SET, invite.id)
