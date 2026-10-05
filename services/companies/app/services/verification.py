from prepza_common.user import User

from app.helpers.verification import email_on_domain
from app.models.companies import Company
from app.storage import companies


async def verify_by_email(company: Company, user: User) -> None:
    """Verifies the company's website domain when this owner or admin signed in with a verified
    email on it; the company row is updated in place."""
    domain = company.website_domain

    verifies = (
        domain is not None
        and not company.verified_domain
        and user.email_verified
        and email_on_domain(user.email, domain)
    )

    if verifies:
        await companies.set_website(company.id, domain, verified=True)
        company.verified_domain = domain
