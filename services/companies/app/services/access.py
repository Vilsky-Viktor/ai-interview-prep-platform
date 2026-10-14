from uuid import UUID

from fastapi import HTTPException, Request, status
from prepza_common.auth import CurrentUser

from app.constants.ai_apps import AI_APPS_OFF
from app.constants.audit import VIA_MCP
from app.constants.invites import COMPANY_SUSPENDED, INTERVIEW_UNAVAILABLE, InviteStatus
from app.constants.roles import EDITORS, Role
from app.models.companies import Company, Member
from app.service_auth import REQUEST_VIA
from app.storage import companies


async def require_company(user: CurrentUser, company_id: UUID) -> tuple[Company, Member]:
    """Any member: owners, admins and viewers. Enough for reading."""
    company = await companies.get(company_id)

    if company is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")

    member = member_of(company, user.uid)

    if member is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")

    # An AI app a member connected, while its owners and admins don't allow them.
    if REQUEST_VIA.get() == VIA_MCP and company.ai_apps_off_at is not None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, AI_APPS_OFF)

    return company, member


def member_of(company: Company, user_id: str) -> Member | None:
    return next((item for item in company.members if item.user_id == user_id), None)


def can_edit(member: Member) -> bool:
    return member.role in EDITORS


# Only the owner deletes the company and manages its members.
def is_owner(member: Member) -> bool:
    return member.role == Role.OWNER


async def require_editor(user: CurrentUser, company_id: UUID) -> tuple[Company, Member]:
    """An owner or admin: everything that changes the company or spends its credits."""
    company, member = await require_company(user, company_id)

    if not can_edit(member):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Viewers can't change anything here")

    # Suspended by a superadmin: it can still be read (and deleted by its owner), not changed.
    if company.suspended_at is not None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, COMPANY_SUSPENDED)

    return company, member


def refuse_if_suspended(company: Company | None, invite_status: str | None) -> None:
    """For a candidate: a suspended company's interview isn't available (410), unless they're
    already in it, which they may finish."""
    suspended = company is not None and company.suspended_at is not None

    if suspended and invite_status != InviteStatus.IN_PROCESS:
        raise HTTPException(status.HTTP_410_GONE, INTERVIEW_UNAVAILABLE)


def bearer_token(request: Request) -> str:
    header = request.headers.get("authorization", "")

    return header.removeprefix("Bearer ").removeprefix("bearer ")
