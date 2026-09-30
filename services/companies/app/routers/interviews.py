from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, Request, status

from app.auth import CurrentUser
from app.constants.events import CANDIDATE_INVITED
from app.constants.invites import InviteStatus
from app.constants.roles import Role
from app.helpers.interviews import attach_set, interview_out, topics_out
from app.integrations import generation as generation_api
from app.integrations import library, rounds
from app.integrations.events import publish
from app.schemas.interviews import (
    InterviewCreate,
    InterviewDetail,
    InterviewOut,
    InterviewSettings,
    TitleIn,
)
from app.schemas.invites import CandidateIn, CandidateOut
from app.services.access import bearer_token, require_company
from app.storage import interviews, invites

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_interview(
    body: InterviewCreate, company_id: UUID, user: CurrentUser, request: Request
) -> InterviewOut:
    company, _ = await require_company(user, company_id)

    try:
        created = await generation_api.create(body.text, company.id, bearer_token(request))
    except httpx.HTTPStatusError as error:
        if error.response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS, "Too many requests. Try again later."
            )

        raise

    interview = await interviews.create(
        company.id, created["id"], body.mode, body.share_results
    )

    return await interview_out(interview)


@router.get("")
async def list_interviews(company_id: UUID, user: CurrentUser) -> list[InterviewOut]:
    company, _ = await require_company(user, company_id)

    return [await interview_out(item) for item in await interviews.list_for_company(company.id)]


@router.get("/{interview_id}")
async def get_interview(interview_id: UUID, user: CurrentUser) -> InterviewDetail:
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    await require_company(user, interview.company_id)

    base = await interview_out(interview)
    found = await library.get_set(interview.set_id) if interview.set_id else None

    topics = topics_out(found, interview.topic_limits) if found else []

    return InterviewDetail(**base.model_dump(), topics=topics)


@router.patch("/{interview_id}/settings", status_code=status.HTTP_204_NO_CONTENT)
async def update_settings(
    interview_id: UUID, body: InterviewSettings, user: CurrentUser
) -> None:
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    _, member = await require_company(user, interview.company_id)

    if member.role not in (Role.OWNER, Role.ADMIN):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can't change this interview")

    await interviews.update_settings(interview.id, body.mode, body.share_results)


@router.patch("/{interview_id}/title", status_code=status.HTTP_204_NO_CONTENT)
async def rename_interview(interview_id: UUID, body: TitleIn, user: CurrentUser) -> None:
    """Company owners and admins can rename an interview once it has been generated."""
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    _, member = await require_company(user, interview.company_id)

    if member.role not in (Role.OWNER, Role.ADMIN):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can't rename this interview")

    if interview.set_id is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Interview is still being generated")

    await library.rename_set(interview.set_id, body.title)


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

    email = str(body.email).lower()
    invite = await invites.upsert(interview.id, email)
    title = (await library.get_set(interview.set_id) or {}).get("title") or "an interview"
    await publish(
        CANDIDATE_INVITED,
        {
            "email": invite.email,
            "token": invite.token,
            "title": title,
            "company": company.name,
        },
    )

    return CandidateOut(
        id=invite.id, email=invite.email, status=invite.status, created_at=invite.created_at
    )


@router.get("/{interview_id}/candidates")
async def list_candidates(interview_id: UUID, user: CurrentUser) -> list[CandidateOut]:
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    await require_company(user, interview.company_id)
    totals = await rounds.invite_scores([invite.id for invite in interview.invites])
    finished = [
        invite.id
        for invite in interview.invites
        if (totals.get(str(invite.id)) or {}).get("finished")
        and invite.status != InviteStatus.FINISHED
    ]

    if finished:
        await invites.set_status(finished, InviteStatus.FINISHED)

        for invite in interview.invites:
            if invite.id in finished:
                invite.status = InviteStatus.FINISHED

    return [
        CandidateOut(
            id=invite.id,
            email=invite.email,
            status=invite.status,
            progress=(totals.get(str(invite.id)) or {}).get("progress", 0),
            grade=(totals.get(str(invite.id)) or {}).get("grade"),
            created_at=invite.created_at,
        )
        for invite in interview.invites
    ]


@router.get("/{interview_id}/candidates/{invite_id}")
async def candidate_scorecard(interview_id: UUID, invite_id: UUID, user: CurrentUser) -> dict:
    interview = await interviews.get(interview_id)
    invite = next((item for item in (interview.invites if interview else []) if item.id == invite_id), None)

    if interview is None or invite is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate not found")

    await require_company(user, interview.company_id)

    card = await rounds.scorecard(invite.id) or []

    if card and all(item["status"] == "finished" for item in card):
        if invite.status != InviteStatus.FINISHED:
            await invites.set_status([invite.id], InviteStatus.FINISHED)
            invite.status = InviteStatus.FINISHED

    return {
        "id": str(invite.id),
        "email": invite.email,
        "status": invite.status,
        "sessions": card,
    }
