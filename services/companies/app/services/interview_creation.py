import httpx
from fastapi import HTTPException, status
from prepza_common.analytics import track
from prepza_common.constants import DAY_SECONDS
from prepza_common.rate_limit import hit

from app.constants.invites import (
    INTERVIEWS_PER_DAY,
    INTERVIEWS_PER_DAY_UNPAID,
    MAX_INTERVIEWS_WITHOUT_CANDIDATES,
    MAX_INTERVIEWS_WITHOUT_CANDIDATES_UNPAID,
    TOO_MANY_INTERVIEWS,
    TOO_MANY_INTERVIEWS_UNPAID,
    TOO_MANY_WITHOUT_CANDIDATES,
    TOO_MANY_WITHOUT_CANDIDATES_UNPAID,
)
from app.helpers.interviews import interview_out
from app.integrations import billing
from app.integrations import generation as generation_api
from app.integrations.redis import get_redis
from app.models.companies import Company
from app.schemas.interviews import InterviewOut
from app.storage import interviews


async def create(
    company: Company, user_id: str, language: str | None, text: str, generate_in: str | None
) -> InterviewOut:
    """Starts making an interview from a job description, as `user_id`, an owner or admin (on
    the site or through the API; each checks the pause first): refused past the company's
    interviews without candidates and past its interviews a day (fewer until it tops up)."""
    # A company that ever topped up gets more (the costs are covered by its candidates).
    paid = await billing.company_paid(company.id)
    waiting = (
        MAX_INTERVIEWS_WITHOUT_CANDIDATES if paid else MAX_INTERVIEWS_WITHOUT_CANDIDATES_UNPAID
    )

    # Checked first, so a refused attempt doesn't count towards the day's limit.
    if await interviews.without_candidates(company.id) >= waiting:
        await track(
            "limit_hit",
            user_id=user_id,
            company_id=company.id,
            which="interviews_without_candidates",
        )

        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            TOO_MANY_WITHOUT_CANDIDATES if paid else TOO_MANY_WITHOUT_CANDIDATES_UNPAID,
        )

    try:
        await hit(
            get_redis(),
            f"rate:interviews:{company.id}",
            INTERVIEWS_PER_DAY if paid else INTERVIEWS_PER_DAY_UNPAID,
            DAY_SECONDS,
            TOO_MANY_INTERVIEWS if paid else TOO_MANY_INTERVIEWS_UNPAID,
        )
    except HTTPException:
        await track("limit_hit", user_id=user_id, company_id=company.id, which="interviews_a_day")
        raise

    try:
        created = await generation_api.create(
            text, company.id, user_id, language, generate_in, paid
        )
    except httpx.HTTPStatusError as error:
        if error.response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS, "Too many requests. Try again later."
            )

        raise

    # Generation picks the language from the job description, not from the recruiter's interface.
    interview = await interviews.create(company.id, created["id"], created["language"])

    return await interview_out(interview)
