import asyncio

from firebase_admin import auth as firebase_auth
from prepza_common import http, memory_cache
from prepza_common.auth import verify
from prepza_common.user import User

from app.config.settings import settings

# Kept until this long before Firebase says it expires.
EXPIRY_MARGIN_SECONDS = 300
CACHE_KEY = "mcp:id-token:{uid}"
IDENTITY_TOOLKIT = "https://identitytoolkit.googleapis.com/v1"


def identity_url() -> str:
    """Firebase's sign-in API: the Auth emulator's locally."""
    if settings.firebase_auth_emulator_host:
        return f"http://{settings.firebase_auth_emulator_host}/identitytoolkit.googleapis.com/v1"

    return IDENTITY_TOOLKIT


async def sign_in(uid: str) -> tuple[User, str] | None:
    """The user and a Firebase ID token of theirs, as if they had signed in: an AI app's calls
    go to the other services with it, which check it as any user's. Kept in memory until shortly
    before it expires. None when the account is gone or disabled; never for an unknown uid (a
    custom token would create that user)."""
    cached = memory_cache.get(CACHE_KEY.format(uid=uid))

    if cached is not None:
        return cached

    try:
        account = await asyncio.to_thread(firebase_auth.get_user, uid)
    except firebase_auth.UserNotFoundError:
        return None

    if account.disabled:
        return None

    custom = await asyncio.to_thread(firebase_auth.create_custom_token, uid)
    response = await http.get_client().post(
        f"{identity_url()}/accounts:signInWithCustomToken",
        params={"key": settings.firebase_web_api_key},
        json={"token": custom.decode(), "returnSecureToken": True},
    )
    response.raise_for_status()
    found = response.json()
    user = verify(found["idToken"])

    if user is None:
        return None

    seconds = int(found["expiresIn"]) - EXPIRY_MARGIN_SECONDS
    memory_cache.put(CACHE_KEY.format(uid=uid), (user, found["idToken"]), seconds)

    return user, found["idToken"]


def forget(uid: str) -> None:
    """Drops the user's kept token, so the next call signs in again (their language changed)."""
    memory_cache.put(CACHE_KEY.format(uid=uid), None, 0)
