from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query
from prepza_common.auth import CurrentUser
from prepza_common.paging import PageParams

from app.constants.invites import MAX_SEARCH_LENGTH
from app.schemas.invites import CompanyCandidateOut
from app.services import candidate_results
from app.services.access import require_company

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/{company_id}/candidates")
async def search_candidates(
    company_id: UUID,
    user: CurrentUser,
    page: PageParams,
    q: Annotated[str, Query(max_length=MAX_SEARCH_LENGTH)] = "",
) -> list[CompanyCandidateOut]:
    """The company's candidates across its interviews, newest first, a page at a time; `q`
    narrows them to an email or name containing it. Any member, viewers too."""
    company, _ = await require_company(user, company_id)

    return await candidate_results.company_page(company.id, page.offset, page.limit, q.strip())
