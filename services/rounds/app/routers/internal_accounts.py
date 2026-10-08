from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder

from app.schemas.sessions import InviteIdsIn
from app.service_auth import ServiceCaller
from app.storage import accounts, sessions

router = APIRouter(prefix="/internal", tags=["internal"])


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, caller: ServiceCaller) -> None:
    """Part of deleting an account (library coordinates it); safe to repeat."""
    await accounts.delete_user(user_id)


@router.post("/users/{user_id}/export")
async def export_user(user_id: str, caller: ServiceCaller) -> dict:
    return jsonable_encoder(await accounts.export(user_id))


@router.post("/invites/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invite_sessions(body: InviteIdsIn, caller: ServiceCaller) -> None:
    """Companies' retention: candidates' sessions go with their expired invites."""
    await sessions.remove_for_invites(body.invite_ids)
