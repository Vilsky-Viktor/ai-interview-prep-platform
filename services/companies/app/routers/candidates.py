import asyncio
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Query, status
from prepza_common.analytics import track
from prepza_common.auth import CurrentUser
from prepza_common.paging import PageParams
from prepza_common.pause import refuse_if_paused

from app.constants.audit import VIA_ASSISTANT, AuditAction
from app.constants.invites import (
    EXTRA_TIME_OPTIONS,
    MAX_SEARCH_LENGTH,
    NOT_STARTED,
    CandidateFilter,
    CandidateSort,
    InviteStatus,
)
from app.helpers.candidates import passed, section_passed
from app.helpers.interviews import (
    attach_set,
    interview_title,
)
from app.helpers.logos import logo_path
from app.integrations import rounds
from app.integrations.redis import get_redis
from app.schemas.invites import CandidateFiltersOut, CandidateIn, CandidateNameIn, CandidateOut
from app.schemas.scorecards import ScorecardOut
from app.service_auth import from_assistant
from app.services import candidate_invites, candidate_results
from app.services import outbox as outbox_service
from app.services.access import can_edit, require_company, require_editor
from app.services.candidate_billing import settle_removed
from app.storage import audit, candidates, interviews, invites

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("/{interview_id}/candidates", status_code=status.HTTP_201_CREATED)
async def invite_candidate(
    interview_id: UUID, body: CandidateIn, user: CurrentUser
) -> CandidateOut:
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    company, _ = await require_editor(user, interview.company_id)
    # Paused, no invite (new or sent again) goes out: its candidate couldn't start.
    await refuse_if_paused(get_redis())
    interview = await attach_set(interview)

    if interview.set_id is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Interview is still being generated")

    invite = await candidate_invites.invite(interview, company, user, str(body.email), body.name)
    await outbox_service.flush_quietly()

    return CandidateOut(
        id=invite.id,
        email=invite.email,
        name=invite.name,
        status=invite.status,
        created_at=invite.created_at,
    )


@router.get("/candidates/filters")
def candidate_filters() -> CandidateFiltersOut:
    """What candidates can be filtered by."""
    return CandidateFiltersOut(filters=list(CandidateFilter))


@router.get("/{interview_id}/candidates")
async def list_candidates(
    interview_id: UUID,
    user: CurrentUser,
    page: PageParams,
    sort: CandidateSort = CandidateSort.GRADE,
    q: Annotated[str, Query(max_length=MAX_SEARCH_LENGTH)] = "",
    filter_by: Annotated[CandidateFilter | None, Query(alias="status")] = None,
) -> list[CandidateOut]:
    """A page at a time (candidate_results.page)."""
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    await require_company(user, interview.company_id)
    by_grade = sort == CandidateSort.GRADE

    return await candidate_results.page(
        interview, page.offset, page.limit, by_grade, q.strip(), filter_by
    )


@router.delete("/{interview_id}/candidates/{invite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_candidate(interview_id: UUID, invite_id: UUID, user: CurrentUser) -> None:
    """Withdraws an invite the candidate hasn't used yet. Once they've started, it erases them for
    good, answers and results included, for example when they ask to have their data deleted.
    A candidate who answered at least one question is charged; other credits still held come
    back."""
    interview = await interviews.get(interview_id)
    invite = await candidates.get(interview_id, invite_id) if interview else None

    if interview is None or invite is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate not found")

    await require_editor(user, interview.company_id)

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
    await audit.record(interview.company_id, user.uid, action, invite.id)


@router.patch("/{interview_id}/candidates/{invite_id}/name", status_code=status.HTTP_204_NO_CONTENT)
async def rename_candidate(
    interview_id: UUID, invite_id: UUID, body: CandidateNameIn, user: CurrentUser
) -> None:
    """Owners and admins correct the name a candidate's sign-in gave, a nickname for example; a
    blank name makes it not known. The sign-in fills only a name not known, so this one stays."""
    interview = await interviews.get(interview_id)
    invite = await candidates.get(interview_id, invite_id) if interview else None

    if interview is None or invite is None or invite.status == InviteStatus.DELETED:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate not found")

    await require_editor(user, interview.company_id)
    await candidates.set_name(invite.id, body.name or None)


@router.get("/{interview_id}/candidates/{invite_id}")
async def candidate_scorecard(
    interview_id: UUID,
    invite_id: UUID,
    user: CurrentUser,
    x_assistant: Annotated[str | None, Header(include_in_schema=False)] = None,
) -> ScorecardOut:
    """A view through the in-app assistant (a valid X-Assistant token) is audited as via the
    assistant and isn't the funnel's "results viewed"."""
    interview = await interviews.get(interview_id)
    invite = await candidates.get(interview_id, invite_id) if interview else None

    if interview is None or invite is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate not found")

    company, member = await require_company(user, interview.company_id)
    # Both from rounds, asked at once.
    card, scores = await asyncio.gather(
        rounds.scorecard(invite.id), rounds.invite_scores([invite.id])
    )
    card = card or []
    totals = scores.get(str(invite.id)) or {}
    await candidate_results.sync([invite], {str(invite.id): totals})

    # The funnel's "first results viewed": a finished candidate's results, opened by a member
    # (not the assistant). The audit row is written whatever happens to the funnel event, which
    # never raises.
    if invite.status == InviteStatus.FINISHED and from_assistant(x_assistant):
        await audit.record(
            company.id, user.uid, AuditAction.RESULTS_VIEWED, invite.id, via=VIA_ASSISTANT
        )
    elif invite.status == InviteStatus.FINISHED:
        await asyncio.gather(
            track("results_viewed", user_id=user.uid, company_id=company.id),
            audit.record(company.id, user.uid, AuditAction.RESULTS_VIEWED, invite.id),
        )

    return ScorecardOut(
        id=invite.id,
        email=invite.email,
        name=invite.name,
        status=invite.status,
        extra_time=invite.extra_time,
        can_edit=can_edit(member),
        extra_time_options=(
            list(EXTRA_TIME_OPTIONS) if invite.status in NOT_STARTED and can_edit(member) else []
        ),
        title=await interview_title(interview),
        company=company.name,
        logo_url=logo_path(company),
        verified_domain=company.verified_domain,
        grade=totals.get("grade"),
        passed=passed(totals, interview.pass_mark),
        pass_mark=interview.pass_mark,
        sessions=[
            {**section, "passed": section_passed(section, interview.pass_mark)} for section in card
        ],
    )
