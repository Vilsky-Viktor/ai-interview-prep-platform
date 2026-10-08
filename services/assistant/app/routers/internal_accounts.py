from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from prepza_common.user import UserEmailIn

from app.service_auth import ServiceCaller
from app.storage import actions, conversations, messages

router = APIRouter(prefix="/internal", tags=["internal"])


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, body: UserEmailIn, caller: ServiceCaller) -> None:
    """Library, deleting an account: their conversations go, with every message and tool call,
    and the actions they hadn't confirmed yet. Safe to repeat."""
    await conversations.delete_user(user_id)
    await actions.delete_user(user_id)


@router.post("/users/{user_id}/export")
async def export_user(user_id: str, body: UserEmailIn, caller: ServiceCaller) -> dict:
    """Library, for "Download my data": their conversations and messages (text, and the ids
    their blocks refer to)."""
    return jsonable_encoder({"assistant_conversations": await messages.export(user_id)})
