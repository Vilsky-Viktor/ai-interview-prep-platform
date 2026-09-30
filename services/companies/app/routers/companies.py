from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.auth import CurrentUser
from app.constants.roles import Role
from app.models.companies import Company
from app.schemas.companies import CompanyCreate, CompanyOut
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
    company = await companies.create(body.name.strip(), user.uid, user.email)

    return CompanyOut(
        id=company.id,
        name=company.name,
        role="owner",
        interview_count=0,
        created_at=company.created_at,
    )


@router.get("")
async def list_companies(user: CurrentUser) -> list[CompanyOut]:
    rows = await companies.list_for_user(user.uid)
    totals = await interviews.counts([item.id for item in rows])

    return [company_out(item, user.uid, totals.get(item.id, 0)) for item in rows]


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(company_id: UUID, user: CurrentUser) -> None:
    """Removing a company deletes its interviews and invites. Only the owner can do it."""
    _, member = await require_company(user, company_id)

    if member.role != Role.OWNER:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the owner can remove the company")

    await companies.delete(company_id)


@router.get("/{company_id}")
async def get_company(company_id: UUID, user: CurrentUser) -> CompanyOut:
    company, _ = await require_company(user, company_id)
    totals = await interviews.counts([company.id])

    return company_out(company, user.uid, totals.get(company.id, 0))
