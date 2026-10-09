from uuid import UUID

from fastapi import APIRouter, status
from prepza_common.paging import PageParams

from app.auth import ApiKeyDep
from app.config.settings import settings
from app.helpers.public import candidate_of, interview_of
from app.integrations import companies
from app.schemas.public import Candidate, CandidateIn, Interview

# Every route can answer these; ones under an interview also 404 (NOT_FOUND).
router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"],
    responses={
        401: {
            "description": "The API key is missing, invalid or expired, or its creator can no longer use it"
        },
        429: {"description": "Your company's keys exceeded 60 requests per minute"},
    },
)
NOT_FOUND = {404: {"description": "The interview or candidate doesn't exist in your company"}}


@router.get("", summary="List interviews")
async def list_interviews(key: ApiKeyDep, page: PageParams) -> list[Interview]:
    """Returns your company's interviews, newest first."""
    found = await companies.interviews(key.company_id, page.offset, page.limit)

    return [interview_of(item) for item in found]


@router.get("/{interview_id}", summary="Get an interview", responses=NOT_FOUND)
async def get_interview(interview_id: UUID, key: ApiKeyDep) -> Interview:
    """Returns one of your company's interviews."""
    return interview_of(await companies.interview(key.company_id, interview_id))


@router.get(
    "/{interview_id}/candidates",
    summary="List candidates",
    tags=["Candidates"],
    responses=NOT_FOUND,
)
async def list_candidates(interview_id: UUID, key: ApiKeyDep, page: PageParams) -> list[Candidate]:
    """Returns the interview's candidates with their progress and results, newest first."""
    found = await companies.candidates(key.company_id, interview_id, page.offset, page.limit)

    return [candidate_of(item, key.company_id, interview_id, settings.site_url) for item in found]


@router.get(
    "/{interview_id}/candidates/{candidate_id}",
    summary="Get a candidate",
    tags=["Candidates"],
    responses=NOT_FOUND,
)
async def get_candidate(interview_id: UUID, candidate_id: UUID, key: ApiKeyDep) -> Candidate:
    """Returns one candidate of the interview with their progress and results."""
    found = await companies.candidate(key.company_id, interview_id, candidate_id)

    return candidate_of(found, key.company_id, interview_id, settings.site_url)


@router.post(
    "/{interview_id}/candidates",
    status_code=status.HTTP_201_CREATED,
    summary="Invite a candidate",
    tags=["Candidates"],
    responses={
        **NOT_FOUND,
        402: {"description": "The company doesn't have enough credits"},
        409: {"description": "The interview's questions are still being generated"},
        429: {
            "description": "The key's creator reached their email limits, or the key its rate limit"
        },
        503: {"description": "Invitations are temporarily paused"},
    },
)
async def invite_candidate(interview_id: UUID, body: CandidateIn, key: ApiKeyDep) -> Candidate:
    """Emails the candidate an invitation to the interview on behalf of the key's creator and
    reserves credits for them, with their name if given. Inviting an address that was already
    invited sends the invitation again."""
    await companies.interview(key.company_id, interview_id)
    invite_id = await companies.invite(interview_id, str(body.email), key.created_by, body.name)
    found = await companies.candidate(key.company_id, interview_id, invite_id)

    return candidate_of(found, key.company_id, interview_id, settings.site_url)
