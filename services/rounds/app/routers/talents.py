from fastapi import APIRouter
from prepza_common.auth import CurrentUser

from app.schemas.talents import TalentLinkIn, TalentLinkOut
from app.storage import talents

# Being suggested to companies: asked once, before a talent's first practice round. They share a
# LinkedIn link, or decline; later they change it in their settings.
router = APIRouter(prefix="/talent-link", tags=["talents"])


@router.get("")
async def get_link(user: CurrentUser) -> TalentLinkOut:
    found = await talents.get(user.uid)

    return TalentLinkOut(decided=found is not None, url=found.url if found else None)


@router.put("")
async def save_link(body: TalentLinkIn, user: CurrentUser) -> TalentLinkOut:
    """A link is the consent: companies may see the talent's name, this link and their first
    practice score on templates for roles like theirs. No link declines, or withdraws at once."""
    saved = await talents.save(
        user.uid, user.name or user.email, str(body.url) if body.url else None
    )

    return TalentLinkOut(decided=True, url=saved.url)
