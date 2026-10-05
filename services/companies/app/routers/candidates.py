from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from prepza_common.analytics import track
from prepza_common.auth import CurrentUser
from prepza_common.paging import PageParams

from app.constants.invites import (
    MAX_SEARCH_LENGTH,
    NOT_STARTED,
    RESULT_FILTERS,
    CandidateFilter,
    CandidateSort,
    InviteStatus,
)
from app.helpers.candidates import (
    by_grade,
    candidate_key,
    candidate_out,
    flagged,
    passed,
    section_passed,
)
from app.helpers.interviews import (
    attach_set,
    interview_title,
)
from app.helpers.logos import logo_path
from app.integrations import billing, rounds
from app.schemas.invites import CandidateFiltersOut, CandidateIn, CandidateOut
from app.services import candidate_invites
from app.services import outbox as outbox_service
from app.services.access import require_company
from app.storage import interviews, invites

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("/{interview_id}/candidates", status_code=status.HTTP_201_CREATED)
async def invite_candidate(
    interview_id: UUID, body: CandidateIn, user: CurrentUser
) -> CandidateOut:
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    company, _ = await require_company(user, interview.company_id)

    interview = await attach_set(interview)

    if interview.set_id is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Interview is still being generated")

    invite = await candidate_invites.invite(interview, company, user, str(body.email))
    await outbox_service.flush_quietly()

    return CandidateOut(
        id=invite.id, email=invite.email, status=invite.status, created_at=invite.created_at
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
    """A page at a time, best grade first or newest first, narrowed to an email containing `q`
    and a status or result. Results come from rounds: for every candidate when sorting or
    filtering by them, otherwise for this page only."""
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    await require_company(user, interview.company_id)
    status_is = None if filter_by in RESULT_FILTERS else filter_by

    if sort == CandidateSort.GRADE or filter_by in RESULT_FILTERS:
        every = await invites.list_all_for_interview(interview.id, q.strip(), status_is)
        totals = await rounds.invite_scores([invite.id for invite in every])

        if filter_by == CandidateFilter.PASSED:
            every = [
                invite
                for invite in every
                if passed(totals.get(str(invite.id)) or {}, interview.pass_mark)
            ]
        elif filter_by == CandidateFilter.FLAGGED:
            every = [invite for invite in every if flagged(totals.get(str(invite.id)) or {})]

        if sort == CandidateSort.GRADE:
            every = by_grade(every, totals)

        listed = every[page.offset : page.offset + page.limit]
    else:
        listed = await invites.list_for_interview(
            interview.id, page.offset, page.limit, q.strip(), status_is
        )
        totals = await rounds.invite_scores([invite.id for invite in listed])
    finished = [
        invite.id
        for invite in listed
        if (totals.get(str(invite.id)) or {}).get("finished")
        and invite.status != InviteStatus.FINISHED
    ]

    if finished:
        await invites.set_status(finished, InviteStatus.FINISHED)

        for invite in listed:
            if invite.id in finished:
                invite.status = InviteStatus.FINISHED

    return [candidate_out(invite, totals.get(str(invite.id)) or {}, interview) for invite in listed]


@router.delete("/{interview_id}/candidates/{invite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_candidate(interview_id: UUID, invite_id: UUID, user: CurrentUser) -> None:
    """Withdraws an invite the candidate hasn't used yet; later it would discard their answers."""
    interview = await interviews.get(interview_id)
    invite = next(
        (item for item in (interview.invites if interview else []) if item.id == invite_id), None
    )

    if interview is None or invite is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate not found")

    await require_company(user, interview.company_id)

    if invite.status not in NOT_STARTED:
        raise HTTPException(status.HTTP_409_CONFLICT, "The candidate has already started")

    await billing.release_candidate(candidate_key(interview.id, invite.email))
    await invites.remove(invite.id)


@router.get("/{interview_id}/candidates/{invite_id}")
async def candidate_scorecard(interview_id: UUID, invite_id: UUID, user: CurrentUser) -> dict:
    interview = await interviews.get(interview_id)
    invite = next(
        (item for item in (interview.invites if interview else []) if item.id == invite_id), None
    )

    if interview is None or invite is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate not found")

    company, _ = await require_company(user, interview.company_id)
    card = await rounds.scorecard(invite.id) or []
    totals = (await rounds.invite_scores([invite.id])).get(str(invite.id)) or {}

    finished = card and all(item["status"] == "finished" for item in card)

    if finished and invite.status != InviteStatus.FINISHED:
        await invites.set_status([invite.id], InviteStatus.FINISHED)
        invite.status = InviteStatus.FINISHED

    # The funnel's "first results viewed": a finished candidate's results, opened by a member.
    if invite.status == InviteStatus.FINISHED:
        await track("results_viewed", user_id=user.uid, company_id=company.id)

    return {
        "id": str(invite.id),
        "email": invite.email,
        "status": invite.status,
        # For the PDF report: the test, the company, and the overall result.
        "title": await interview_title(interview),
        "company": company.name,
        "logo_url": logo_path(company),
        "verified_domain": company.verified_domain,
        "grade": totals.get("grade"),
        "passed": passed(totals, interview.pass_mark),
        "pass_mark": interview.pass_mark,
        "sessions": [
            {**section, "passed": section_passed(section, interview.pass_mark)} for section in card
        ],
    }
