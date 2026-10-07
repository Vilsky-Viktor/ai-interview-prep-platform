from uuid import UUID

from fastapi import HTTPException, Request, status
from prepza_common.auth import CurrentUser

from app.constants.roles import EDITORS
from app.models.companies import Company, Member
from app.storage import companies


async def require_company(user: CurrentUser, company_id: UUID) -> tuple[Company, Member]:
    """Any member: owners, admins and viewers. Enough for reading."""
    company = await companies.get(company_id)

    if company is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")

    member = member_of(company, user.uid)

    if member is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")

    return company, member


def member_of(company: Company, user_id: str) -> Member | None:
    return next((item for item in company.members if item.user_id == user_id), None)


def can_edit(member: Member) -> bool:
    return member.role in EDITORS


async def require_editor(user: CurrentUser, company_id: UUID) -> tuple[Company, Member]:
    """An owner or admin: everything that changes the company or spends its credits."""
    company, member = await require_company(user, company_id)

    if not can_edit(member):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Viewers can't change anything here")

    return company, member


def bearer_token(request: Request) -> str:
    header = request.headers.get("authorization", "")

    return header.removeprefix("Bearer ").removeprefix("bearer ")
