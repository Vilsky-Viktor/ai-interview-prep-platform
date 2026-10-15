from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query
from pydantic import EmailStr

from app.auth import ApiKeyDep
from app.config.settings import settings
from app.helpers.public import candidate_of
from app.integrations import companies
from app.schemas.changes import Credits
from app.schemas.public import Candidate

# What's the company's as a whole: its candidates across interviews and its credits.
router = APIRouter(
    tags=["Company"],
    responses={
        401: {
            "description": "The API key is missing, invalid or expired, or its creator can no longer use it"
        },
        429: {"description": "Your company's keys exceeded 60 requests per minute"},
    },
)


@router.get("/candidates", summary="Find a candidate by email")
async def find_candidates(
    email: Annotated[EmailStr, Query(description="The email the candidate was invited with")],
    key: ApiKeyDep,
) -> list[Candidate]:
    """The candidates invited with this email in any of your company's interviews, newest
    first, each with its interview's `interview_id`."""
    found = await companies.find_candidates(key.company_id, str(email))

    rows = [(UUID(row["interview_id"]), UUID(row["candidate_id"])) for row in found]

    return [
        candidate_of(
            await companies.candidate(key.company_id, interview_id, candidate_id),
            key.company_id,
            interview_id,
            settings.site_url,
        )
        for interview_id, candidate_id in rows
    ]


@router.get("/credits", summary="Read your credits")
async def get_credits(key: ApiKeyDep) -> Credits:
    """Your company's credits: a candidate costs 500, set aside when they're invited."""
    return Credits(**await companies.credits(key.company_id))
