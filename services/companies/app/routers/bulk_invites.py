import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser

from app.constants.invites import (
    MAX_BULK_INVITES,
    NO_EMAILS,
    SKIP_REASONS,
    TOO_MANY_EMAILS,
    SkipReason,
)
from app.helpers.email_lists import emails_in, is_email
from app.helpers.interviews import attach_set
from app.schemas.invites import BulkInviteIn, BulkInviteOut, SkippedInvite
from app.services import candidate_invites
from app.services import outbox as outbox_service
from app.services.access import require_company
from app.storage import interviews

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("/{interview_id}/candidates/bulk")
async def invite_many(interview_id: UUID, body: BulkInviteIn, user: CurrentUser) -> BulkInviteOut:
    """Invites every email in a pasted or uploaded list, one by one as a single invite would,
    and says who was invited and why the others weren't."""
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    company, _ = await require_company(user, interview.company_id)
    interview = await attach_set(interview)

    if interview.set_id is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Interview is still being generated")

    emails = emails_in(body.text)

    if not emails:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, NO_EMAILS)

    if len(emails) > MAX_BULK_INVITES:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, TOO_MANY_EMAILS)

    invited: list[str] = []
    skipped: list[SkippedInvite] = []
    out_of_credits = False

    for email in emails:
        reason = None

        if out_of_credits:
            reason = SkipReason.NO_CREDITS
        elif not is_email(email):
            reason = SkipReason.INVALID
        else:
            try:
                await candidate_invites.invite(interview, company, user, email)
            except HTTPException as error:
                out_of_credits = error.status_code == status.HTTP_402_PAYMENT_REQUIRED
                reason = SKIP_REASONS.get(error.status_code, SkipReason.FAILED)
            except Exception:
                logger.exception("Couldn't invite a candidate from a list")
                reason = SkipReason.FAILED

        if reason:
            skipped.append(SkippedInvite(email=email, reason=reason))
        else:
            invited.append(email)

    await outbox_service.flush_quietly()

    return BulkInviteOut(invited=invited, skipped=skipped)
