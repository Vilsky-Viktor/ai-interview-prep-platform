from fastapi import APIRouter, Response, status
from fastapi.encoders import jsonable_encoder
from prepza_common.auth import CurrentUser
from prepza_common.superadmin import is_superadmin

from app.schemas.me import MeOut, SettingsIn
from app.services.accounts import delete_account, export_account, set_language

router = APIRouter()


@router.get("/me")
def me(user: CurrentUser) -> MeOut:
    return MeOut(**user.model_dump(), is_superadmin=is_superadmin(user))


@router.put("/me/settings", status_code=status.HTTP_204_NO_CONTENT)
async def update_settings(body: SettingsIn, user: CurrentUser) -> None:
    """Takes effect once the frontend refreshes the user's ID token."""
    await set_language(user, body.language)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(user: CurrentUser) -> None:
    """Deletes the account and everything about it. A company the user alone owns goes too."""
    await delete_account(user)


@router.get("/me/export")
async def export_me(user: CurrentUser, response: Response) -> dict:
    """Everything prepza holds about the user, as one JSON file to download."""
    response.headers["Content-Disposition"] = 'attachment; filename="prepza-data.json"'

    return jsonable_encoder(await export_account(user))
