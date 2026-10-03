from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser
from prepza_common.paging import PageParams

from app.constants.invites import MAX_OWNED_COMPANIES, TOO_MANY_COMPANIES
from app.constants.roles import Role
from app.integrations import billing
from app.models.companies import Company
from app.schemas.companies import (
    CompanyBalanceOut,
    CompanyCreate,
    CompanyCreditsOut,
    CompanyOut,
)
from app.services import company_deletion
from app.services.access import require_company
from app.storage import companies, interviews

router = APIRouter(prefix="/companies", tags=["companies"])


def company_out(company: Company, user_id: str, interview_count: int = 0) -> CompanyOut:
    member = next(item for item in company.members if item.user_id == user_id)

    return CompanyOut(
        id=company.id,
        name=company.name,
        role=member.role,
        interview_count=interview_count,
        created_at=company.created_at,
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_company(body: CompanyCreate, user: CurrentUser) -> CompanyOut:
    if await companies.owned_count(user.uid) >= MAX_OWNED_COMPANIES:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, TOO_MANY_COMPANIES)

    company = await companies.create(body.name.strip(), user.uid, user.email)
    await billing.welcome_company(company.id, user.email)

    return CompanyOut(
        id=company.id,
        name=company.name,
        role="owner",
        interview_count=0,
        created_at=company.created_at,
    )


@router.get("")
async def list_companies(user: CurrentUser, page: PageParams) -> list[CompanyOut]:
    rows = await companies.list_for_user(user.uid, page.offset, page.limit)
    totals = await interviews.counts([item.id for item in rows])

    return [company_out(item, user.uid, totals.get(item.id, 0)) for item in rows]


@router.get("/credits")
async def list_credits(user: CurrentUser, page: PageParams) -> list[CompanyBalanceOut]:
    """The user's companies with their credits; any member may top one up. Declared before
    /{company_id}, which would otherwise take "credits" as an id."""
    rows = await companies.list_for_user(user.uid, page.offset, page.limit)
    credits = await billing.companies_credits([item.id for item in rows]) if rows else {}

    return [
        CompanyBalanceOut(id=item.id, name=item.name, available=credits.get(str(item.id), 0))
        for item in rows
    ]


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(company_id: UUID, user: CurrentUser) -> None:
    """Only the owner can do it."""
    _, member = await require_company(user, company_id)

    if member.role != Role.OWNER:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the owner can remove the company")

    await company_deletion.delete_company(company_id)


@router.get("/{company_id}/credits")
async def get_credits(company_id: UUID, user: CurrentUser) -> CompanyCreditsOut:
    """Candidates the company can still invite; any member may see it."""
    await require_company(user, company_id)

    return CompanyCreditsOut(available=await billing.available_credits(company_id))


@router.get("/{company_id}")
async def get_company(company_id: UUID, user: CurrentUser) -> CompanyOut:
    company, _ = await require_company(user, company_id)
    totals = await interviews.counts([company.id])

    return company_out(company, user.uid, totals.get(company.id, 0))
