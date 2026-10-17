from fastapi import HTTPException, status
from prepza_common.audit_actions import AuditAction, TargetKind

from app.constants.invites import EXTRA_TIME_STARTED, NOT_STARTED, InviteStatus
from app.integrations import rounds
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.services import outbox as outbox_service
from app.services.candidate_billing import settle_removed
from app.storage import audit, candidates, invites


async def remove(
    interview: Interview, invite: CandidateInvite, user_id: str, via: str | None
) -> None:
    """Withdraws an invite the candidate hasn't used yet. Once they've started, it erases them for
    good, answers and results included, for example when they ask to have their data deleted.
    A candidate who answered at least one question is charged; other credits still held come
    back. `user_id`, an owner or admin, is recorded with `via` (assistant, mcp or api)."""
    if invite.status != InviteStatus.FINISHED:
        await settle_removed([invite])

    if invite.status not in NOT_STARTED:
        await rounds.delete_invite_sessions([invite.id])

    removed = await invites.remove(invite, interview.company_id)

    # Started since it was read: the sessions it made go too.
    if invite.status in NOT_STARTED and removed == InviteStatus.IN_PROCESS:
        await rounds.delete_invite_sessions([invite.id])

    await outbox_service.flush_quietly()
    revoked = invite.status in NOT_STARTED
    action = AuditAction.INVITE_REVOKED if revoked else AuditAction.CANDIDATE_DELETED
    await audit.record(
        interview.company_id, user_id, action, invite.id, via=via, target_kind=TargetKind.CANDIDATE
    )


async def rename(
    interview: Interview,
    invite: CandidateInvite,
    name: str | None,
    user_id: str,
    via: str | None = None,
) -> None:
    """Corrects the name a candidate's sign-in gave, a nickname for example; none makes it not
    known. The sign-in fills only a name not known, so this one stays. A deleted candidate is
    404."""
    if invite.status == InviteStatus.DELETED:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate not found")

    await candidates.set_name(invite.id, name or None)
    await audit.record(
        interview.company_id,
        user_id,
        AuditAction.CANDIDATE_RENAMED,
        invite.id,
        via=via,
        target_kind=TargetKind.CANDIDATE,
    )


async def set_extra_time(
    interview: Interview, invite: CandidateInvite, extra_time: int, user_id: str, via: str | None
) -> None:
    """Extra time on each question, until the candidate starts (409 after)."""
    if invite.status not in NOT_STARTED:
        raise HTTPException(status.HTTP_409_CONFLICT, EXTRA_TIME_STARTED)

    await invites.set_extra_time(invite.id, extra_time)
    await audit.record(
        interview.company_id,
        user_id,
        AuditAction.EXTRA_TIME_SET,
        invite.id,
        via=via,
        target_kind=TargetKind.CANDIDATE,
    )
