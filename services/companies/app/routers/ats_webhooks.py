from uuid import UUID

from fastapi import APIRouter, Request, status

from app.services import ats_candidates

router = APIRouter(prefix="/webhooks/ats", tags=["webhooks"])


@router.post("/workable/{link_id}", status_code=status.HTTP_200_OK)
async def workable_event(link_id: UUID, request: Request) -> None:
    """Workable's events for one linked job, signed with the account's token (checked on the raw
    body). Open in maintenance mode like every /webhooks/ route, so no candidate is lost."""
    await ats_candidates.receive_workable(
        link_id, await request.body(), request.headers.get("x-workable-signature", "")
    )


@router.post("/greenhouse/{connection_id}", status_code=status.HTTP_200_OK)
async def greenhouse_event(connection_id: UUID, request: Request) -> None:
    """The company's Greenhouse web hook (stage changes), signed with the connection's secret key
    (the Signature header, checked on the raw body). Greenhouse's ping on saving it is
    answered too."""
    await ats_candidates.receive_greenhouse(
        connection_id, await request.body(), request.headers.get("signature", "")
    )
