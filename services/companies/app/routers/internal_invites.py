from uuid import UUID

from fastapi import APIRouter, status
from prepza_common.user import UserEmailIn

from app.helpers import notifications
from app.schemas.invites import InvitedCompaniesOut
from app.service_auth import ServiceCaller
from app.services import outbox as outbox_service
from app.storage import interviews, invites

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/invites/{invite_id}/undelivered", status_code=status.HTTP_204_NO_CONTENT)
async def invite_undelivered(invite_id: UUID, caller: ServiceCaller) -> None:
    """Notifications reports a bounced or spam-flagged invite email; safe to repeat. The
    company is told."""
    invite = await invites.get(invite_id)

    if invite is None:
        return

    interview = await interviews.get(invite.interview_id)
    await invites.mark_undelivered(
        invite_id, notifications.invite_undelivered(interview, invite.email)
    )
    await outbox_service.flush_quietly()


@router.post("/invites/companies")
async def invited_companies(body: UserEmailIn, caller: ServiceCaller) -> InvitedCompaniesOut:
    """Notifications, for the admin zone's emails tab: the companies that invited the address,
    whose emails to it a superadmin may stop. The address goes in the body, never the query
    string, which request logs record."""
    return InvitedCompaniesOut(company_ids=await invites.company_ids_for(body.email))
