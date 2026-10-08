from uuid import UUID

from prepza_common.company_access import require
from prepza_common.user import User

from app.integrations import companies


async def require_company(user: User, company_id: UUID) -> None:
    """Any member: owners, admins and viewers. Enough for reading."""
    require(await companies.access(company_id, user.uid), editor=False)


async def require_editor(user: User, company_id: UUID) -> None:
    """An owner or admin: everything that changes the company's integrations."""
    require(await companies.access(company_id, user.uid), editor=True)
