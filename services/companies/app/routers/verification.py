from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser

from app.constants.verification import FREE_DOMAIN, NOT_A_WEBSITE
from app.helpers.verification import email_on_domain, is_free_domain, website_domain
from app.schemas.verification import VerificationOut, WebsiteIn
from app.services.access import require_company
from app.storage import companies

# Verified companies: a company is verified for its website's domain once an owner or admin
# signed in with a verified email on that domain. Free mail services never count.
router = APIRouter(prefix="/companies", tags=["verification"])


@router.put("/{company_id}/website")
async def set_website(company_id: UUID, body: WebsiteIn, user: CurrentUser) -> VerificationOut:
    company, _ = await require_company(user, company_id)

    if not body.website.strip():
        await companies.set_website(company.id, None, verified=False)

        return VerificationOut(website_domain=None, verified_domain=None)

    domain = website_domain(body.website)

    if domain is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, NOT_A_WEBSITE)

    if is_free_domain(domain):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, FREE_DOMAIN)

    # Re-saving the same website keeps its verification, whoever saves it.
    verified = company.verified_domain == domain or (
        user.email_verified and email_on_domain(user.email, domain)
    )
    await companies.set_website(company.id, domain, verified)

    return VerificationOut(website_domain=domain, verified_domain=domain if verified else None)
