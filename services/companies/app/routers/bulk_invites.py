import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser
from prepza_common.names import clean_name
from prepza_common.pause import refuse_if_paused

from app.constants.invites import (
    MAX_BULK_INVITES,
    NAME_NEEDS_ONE_EMAIL,
    NO_EMAILS,
    SKIP_REASONS,
    STARTED,
    TOO_MANY_EMAILS,
    SkipReason,
)
from app.helpers.candidate_lists import candidates_in, line_report, unusable_lines
from app.helpers.email_lists import is_email
from app.helpers.interviews import attach_set
from app.helpers.list_files import list_refusal
from app.integrations.redis import get_redis
from app.schemas.invites import BulkInviteIn, BulkInviteOut, SkippedInvite
from app.services import candidate_invites
from app.services import outbox as outbox_service
from app.services.access import require_editor
from app.storage import interviews, invites

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("/{interview_id}/candidates/bulk")
async def invite_many(interview_id: UUID, body: BulkInviteIn, user: CurrentUser) -> BulkInviteOut:
    """Invites every email in a pasted or uploaded list, one by one as a single invite would,
    with the names the list gives ("Name <email>", "email, Name", or a CSV's name columns), and
    says who was invited and why the others weren't."""
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    company, _ = await require_editor(user, interview.company_id)
    # Paused, no invite (new or sent again) goes out: its candidate couldn't start.
    await refuse_if_paused(get_redis())
    interview = await attach_set(interview)

    if interview.set_id is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Interview is still being generated")

    refusal = list_refusal(body.text, body.filename)

    if refusal:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, refusal)

    found = candidates_in(body.text)
    name = clean_name(body.name)

    if not found:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, NO_EMAILS)

    if name and len(found) > 1:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, NAME_NEEDS_ONE_EMAIL)

    # The form's name field wins over a name in the text.
    if name:
        found = [(found[0][0], name)]

    if len(found) > MAX_BULK_INVITES:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, TOO_MANY_EMAILS)

    invited: list[str] = []
    skipped: list[SkippedInvite] = []
    out_of_credits = False

    for email, name in found:
        reason = None

        if out_of_credits:
            reason = SkipReason.NO_CREDITS
        elif not is_email(email):
            reason = SkipReason.INVALID
        elif await invites.status_of(interview.id, email.lower()) in STARTED:
            reason = SkipReason.STARTED
        else:
            try:
                await candidate_invites.invite(interview, company, user, email, name)
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

    no_email, unread_names = unusable_lines(body.text)

    return BulkInviteOut(
        invited=invited,
        skipped=skipped,
        no_email=line_report(no_email),
        unread_names=line_report(unread_names),
    )
