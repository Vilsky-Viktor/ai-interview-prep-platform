from uuid import UUID

from fastapi import HTTPException, Request, status

from app.auth import CurrentUser
from app.constants.roles import Role
from app.models.companies import Company, Member
from app.models.interviews import Interview
from app.storage import companies


async def require_company(user: CurrentUser, company_id: UUID) -> tuple[Company, Member]:
    company = await companies.get(company_id)

    if company is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")

    member = next((item for item in company.members if item.user_id == user.uid), None)

    if member is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")

    return company, member


async def require_manager(user: CurrentUser, interview: Interview) -> None:
    _, member = await require_company(user, interview.company_id)

    if member.role not in (Role.OWNER, Role.ADMIN):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can't change this interview")


def bearer_token(request: Request) -> str:
    header = request.headers.get("authorization", "")

    return header.removeprefix("Bearer ").removeprefix("bearer ")
