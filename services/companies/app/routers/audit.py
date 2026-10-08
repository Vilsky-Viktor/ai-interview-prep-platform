from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser
from prepza_common.paging import PageParams

from app.constants.roles import Role
from app.schemas.audit import AuditEventOut
from app.services.access import require_company
from app.storage import audit

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/{company_id}/audit")
async def list_audit_events(
    company_id: UUID, user: CurrentUser, page: PageParams
) -> list[AuditEventOut]:
    """The company's recorded human decisions, newest first; for the owner only."""
    company, caller = await require_company(user, company_id)

    if caller.role != Role.OWNER:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the owner can see the audit log")

    rows = await audit.list_for_company(company.id, page.offset, page.limit)

    return [
        AuditEventOut(
            user_id=row.user_id,
            action=row.action,
            target_id=row.target_id,
            via=row.via,
            created_at=row.created_at,
        )
        for row in rows
    ]
