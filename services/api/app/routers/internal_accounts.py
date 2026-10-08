from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder

from app.service_auth import ServiceCaller
from app.storage import keys, webhooks

router = APIRouter(prefix="/internal", tags=["internal"], include_in_schema=False)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, email: str, caller: ServiceCaller) -> None:
    """Library, deleting an account: the keys and web hooks they made go."""
    await keys.remove_user(user_id)
    await webhooks.remove_user(user_id)


@router.get("/users/{user_id}/export")
async def export_user(user_id: str, email: str, caller: ServiceCaller) -> dict:
    """Library, for "Download my data": the keys (names only) and web hooks they made."""
    return jsonable_encoder(
        {
            "api_keys": [
                {"company_id": key.company_id, "name": key.name, "at": key.created_at}
                for key in await keys.of_user(user_id)
            ],
            "webhooks": [
                {"company_id": hook.company_id, "url": hook.url, "at": hook.created_at}
                for hook in await webhooks.of_user(user_id)
            ],
        }
    )
