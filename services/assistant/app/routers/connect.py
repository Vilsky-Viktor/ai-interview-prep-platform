from uuid import UUID

from fastapi import APIRouter, status
from prepza_common.auth import CurrentUser

from app.schemas.connect import ConnectionOut, ConnectRequestOut, RedirectOut
from app.services import connections

router = APIRouter(tags=["connect"])


@router.get("/connect/{request_id}")
async def connect_request(request_id: str, user: CurrentUser) -> ConnectRequestOut:
    """An AI app's request to connect to the signed-in user's account, for the consent page; a
    404 once it's answered or expired."""
    return ConnectRequestOut(**await connections.describe(request_id))


@router.post("/connect/{request_id}/approve")
async def approve(request_id: str, user: CurrentUser) -> RedirectOut:
    """The user allows the app to use prepza as them: back to the app with a single-use code."""
    return RedirectOut(redirect_url=await connections.approve(request_id, user))


@router.post("/connect/{request_id}/deny")
async def deny(request_id: str, user: CurrentUser) -> RedirectOut:
    """The user refuses: back to the app, which learns it was denied."""
    return RedirectOut(redirect_url=await connections.deny(request_id))


@router.get("/connections")
async def list_connections(user: CurrentUser) -> list[ConnectionOut]:
    """The AI apps the signed-in user connected, the latest first."""
    return [ConnectionOut.model_validate(grant) for grant in await connections.of_user(user.uid)]


@router.delete("/connections/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect(connection_id: UUID, user: CurrentUser) -> None:
    """Disconnects one of the user's apps: its access stops at once."""
    await connections.disconnect(connection_id, user.uid)
