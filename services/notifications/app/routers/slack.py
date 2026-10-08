from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse
from prepza_common.auth import CurrentUser

from app.schemas.slack import SlackKindsIn, SlackOut, SlackStartOut
from app.services import slack

router = APIRouter(prefix="/slack", tags=["slack"])


@router.get("")
async def get_slack(company_id: str, user: CurrentUser) -> SlackOut:
    """The company's Slack channel and the notifications it gets; every member sees it."""
    await slack.require(company_id, user.uid, editor=False)

    return await slack.overview(company_id)


@router.get("/start")
async def start(company_id: str, user: CurrentUser) -> SlackStartOut:
    """Where "Add to Slack" goes: Slack's page to approve prepza and pick a channel."""
    await slack.require(company_id, user.uid, editor=True)

    return SlackStartOut(url=await slack.start(company_id, user.uid))


@router.get("/callback")
async def callback(state: str, code: str | None = None, error: str | None = None):
    """Slack sends the browser back here; the signed, one-time state says whose company it is.
    Then on to the company's Slack page."""
    return RedirectResponse(await slack.finish(code, state, error), status.HTTP_303_SEE_OTHER)


@router.put("/kinds", status_code=status.HTTP_204_NO_CONTENT)
async def set_kinds(company_id: str, body: SlackKindsIn, user: CurrentUser) -> None:
    await slack.require(company_id, user.uid, editor=True)
    await slack.set_kinds(company_id, body.kinds)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect(company_id: str, user: CurrentUser) -> None:
    await slack.require(company_id, user.uid, editor=True)
    await slack.disconnect(company_id)
