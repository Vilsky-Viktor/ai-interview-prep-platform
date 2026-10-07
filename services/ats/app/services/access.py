from uuid import UUID

from fastapi import HTTPException, status
from prepza_common.user import User

from app.integrations import companies


async def require_company(user: User, company_id: UUID) -> None:
    """Any member: owners, admins and viewers. Enough for reading."""
    found = await companies.access(company_id, user.uid)

    if not found["member"]:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")


async def require_editor(user: User, company_id: UUID) -> None:
    """An owner or admin: everything that changes the company's integrations."""
    found = await companies.access(company_id, user.uid)

    if not found["member"]:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")

    if not found["editor"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Viewers can't change anything here")
