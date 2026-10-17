from fastapi import APIRouter

from app.auth import checked_key
from app.schemas.keys import KeyVerifyIn, VerifiedKeyOut
from app.service_auth import ServiceCaller

router = APIRouter(prefix="/internal/keys", tags=["internal"], include_in_schema=False)


@router.post("/verify")
async def verify_key(body: KeyVerifyIn, caller: ServiceCaller) -> VerifiedKeyOut:
    """The assistant, for an AI agent signing in to the MCP server with a key: checked as the
    API checks it (a 401 for one that doesn't work) and counted against the company's API
    limit (a 429 over it). Whether it may be used there (the mcp permission) is the assistant's
    to decide."""
    found = await checked_key(body.key)

    return VerifiedKeyOut(
        id=found.id,
        company_id=found.company_id,
        created_by=found.created_by,
        permissions=found.permissions,
    )
