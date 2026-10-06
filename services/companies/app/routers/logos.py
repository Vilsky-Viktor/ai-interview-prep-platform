import base64
import binascii
from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status
from prepza_common.auth import CurrentUser

from app.constants.logos import LOGO_CACHE
from app.helpers.logos import logo_path, logo_type
from app.schemas.logos import BrandOut, LogoIn, LogoOut
from app.services.access import require_editor
from app.storage import companies, interviews, invites

# Company branding: the logo candidates see on their pages, emails and reports.
router = APIRouter(tags=["logos"])


@router.put("/companies/{company_id}/logo")
async def set_logo(company_id: UUID, body: LogoIn, user: CurrentUser) -> LogoOut:
    """Any of the company's owners and admins sets the logo: PNG, JPEG or WebP, up to 500 KB."""
    company, _ = await require_editor(user, company_id)

    try:
        content = base64.b64decode(body.image, validate=True)
    except binascii.Error:
        content = b""

    media_type = logo_type(content)

    if media_type is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "Use a PNG, JPEG or WebP image up to 500 KB"
        )

    await companies.set_logo(company.id, content, media_type)

    return LogoOut(logo_url=logo_path(await companies.get(company.id)))


@router.delete("/companies/{company_id}/logo", status_code=status.HTTP_204_NO_CONTENT)
async def remove_logo(company_id: UUID, user: CurrentUser) -> None:
    company, _ = await require_editor(user, company_id)
    await companies.set_logo(company.id, None, None)


@router.get("/companies/{company_id}/logo")
async def get_logo(company_id: UUID) -> Response:
    """Public: candidates' pages and email clients load it without signing in."""
    found = await companies.get_logo(company_id)

    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No logo")

    content, media_type = found

    return Response(
        content,
        media_type=media_type,
        headers={"Cache-Control": LOGO_CACHE, "X-Content-Type-Options": "nosniff"},
    )


@router.get("/candidates/{invite_id}/brand")
async def candidate_brand(invite_id: UUID, user: CurrentUser) -> BrandOut:
    """The company and logo for the candidate taking the interview, or a member previewing it."""
    invite = await invites.get(invite_id)
    interview = await interviews.get(invite.interview_id) if invite else None
    company = await companies.get(interview.company_id) if interview else None
    member = company and any(item.user_id == user.uid for item in company.members)

    if company is None or (invite.user_id != user.uid and not member):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")

    return BrandOut(company=company.name, logo_url=logo_path(company))
