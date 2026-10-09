from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from prepza_common.pause import refuse_if_paused
from prepza_common.user import User

from app.integrations.redis import get_redis
from app.schemas.internal_ats import AccessOut, AtsInviteIn, AtsInviteOut, InterviewBriefOut
from app.service_auth import ServiceCaller
from app.services import candidate_invites
from app.services import outbox as outbox_service
from app.services.access import can_edit, member_of
from app.storage import companies, interviews

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/companies/{company_id}/access")
async def access(company_id: UUID, user_id: str, caller: ServiceCaller) -> AccessOut:
    """What the user may do in the company: ats guards its pages with it. A company that
    doesn't exist is 404."""
    company = await companies.get(company_id)

    if company is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")

    member = member_of(company, user_id)

    return AccessOut(member=member is not None, editor=member is not None and can_edit(member))


@router.get("/interviews")
async def interviews_by_ids(
    ids: Annotated[list[UUID], Query()], caller: ServiceCaller
) -> list[InterviewBriefOut]:
    """The interviews of those ids that still exist, for ats's linked jobs."""
    return [
        InterviewBriefOut(
            id=item.id, company_id=item.company_id, title=item.title, ready=item.set_id is not None
        )
        for item in await interviews.by_ids(ids)
    ]


@router.post("/interviews/{interview_id}/invites", status_code=status.HTTP_201_CREATED)
async def invite(interview_id: UUID, body: AtsInviteIn, caller: ServiceCaller) -> AtsInviteOut:
    """A candidate an ATS sent is invited, as the member who connected it. Refused with 503
    during the emergency pause, 402 without credits and 429 over the email limits; 404 when the
    interview is gone, 409 while it has no questions yet, and 403 when that member is no longer
    an owner or admin (a removed member's connection invites no one)."""
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    if interview.set_id is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "The interview isn't ready yet")

    await refuse_if_paused(get_redis())
    company = await companies.get(interview.company_id)
    sender = member_of(company, body.sender_id)

    if sender is None or not can_edit(sender):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only an owner or admin can invite")

    user = User(uid=body.sender_id, email="", email_verified=True)
    sent = await candidate_invites.invite(interview, company, user, body.email, body.name)
    await outbox_service.flush_quietly()

    return AtsInviteOut(invite_id=sent.id)
