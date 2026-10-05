from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser

from app.helpers.interviews import attach_set
from app.integrations import library, rounds
from app.schemas.talents import HideTalentIn, SuggestedTalentOut
from app.services.access import require_company
from app.storage import interviews, talents

# Suggestions for companies, free: talents who did well practising a template for a role like
# the test's, and agreed to be suggested.
router = APIRouter(prefix="/interviews", tags=["talents"])


async def company_interview(interview_id: UUID, user):
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    await require_company(user, interview.company_id)

    return interview


@router.get("/{interview_id}/suggestions")
async def suggested_talents(interview_id: UUID, user: CurrentUser) -> list[SuggestedTalentOut]:
    interview = await company_interview(interview_id, user)
    interview = await attach_set(interview)

    if interview.set_id is None:
        return []

    template_ids = await library.similar_templates(interview.set_id)

    if not template_ids:
        return []

    hidden = await talents.hidden_urls(interview_id)

    return [
        SuggestedTalentOut(name=talent["name"], url=talent["url"], grade=talent["grade"])
        for talent in await rounds.talent_suggestions(template_ids)
        if talent["url"] not in hidden
    ]


@router.post("/{interview_id}/suggestions/hide", status_code=status.HTTP_204_NO_CONTENT)
async def hide_talent(interview_id: UUID, body: HideTalentIn, user: CurrentUser) -> None:
    """Hides a talent who doesn't fit from this test's suggestions, for everyone in the company."""
    await company_interview(interview_id, user)
    await talents.hide(interview_id, body.url)
