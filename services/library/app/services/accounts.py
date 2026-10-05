import asyncio

from firebase_admin import auth as firebase_auth
from prepza_common.analytics import track
from prepza_common.constants import LANGUAGE_CLAIM
from prepza_common.user import Language, User

from app.integrations import accounts as services
from app.storage import accounts


def delete_sign_in(user_id: str) -> None:
    try:
        firebase_auth.delete_user(user_id)
    except firebase_auth.UserNotFoundError:
        pass


async def set_language(user: User, language: Language) -> None:
    """Stored on the sign-in, so every service reads it from the user's next ID token. A new
    account sets it on its first sign-in (the frontend does), which counts as signing up."""
    record = await asyncio.to_thread(firebase_auth.get_user, user.uid)
    await asyncio.to_thread(
        firebase_auth.set_custom_user_claims, user.uid, {LANGUAGE_CLAIM: language}
    )

    if LANGUAGE_CLAIM not in (record.custom_claims or {}):
        await track("signed_up", user_id=user.uid, language=language)


async def delete_account(user: User) -> None:
    """Deletes everything about the user, in every service, then their sign-in.

    Each step is safe to repeat and raises on failure, so a failed deletion is retried whole and
    the sign-in, which lets the user retry, goes last.
    """
    for service in services.services():
        await services.delete_user(service, user.uid, user.email)

    await accounts.delete_user(user.uid)
    await asyncio.to_thread(delete_sign_in, user.uid)


async def export_account(user: User) -> dict:
    exports = await asyncio.gather(
        *(services.export_user(name, user.uid, user.email) for name in services.services())
    )

    return {
        "account": {
            "id": user.uid,
            "email": user.email,
            "name": user.name,
            "language": user.language,
        },
        "library": await accounts.export(user.uid),
        **dict(zip(services.services(), exports, strict=True)),
    }
