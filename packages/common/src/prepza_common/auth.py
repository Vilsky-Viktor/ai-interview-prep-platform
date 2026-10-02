from typing import Annotated

import sentry_sdk
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth
from prepza_common.constants import SIGN_IN_UNAVAILABLE
from prepza_common.user import User

bearer = HTTPBearer()
optional_bearer = HTTPBearer(auto_error=False)


def verify(token: str) -> User | None:
    """The user a Firebase ID token belongs to, or None when it isn't valid.

    When Google's signing certificates can't be fetched, no token can be checked: that's our
    outage, not a bad token, so it's a 503 rather than a 401.
    """
    try:
        claims = firebase_auth.verify_id_token(token)
    except (ValueError, firebase_auth.InvalidIdTokenError):
        return None
    except firebase_auth.CertificateFetchError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, SIGN_IN_UNAVAILABLE)

    return User(
        uid=claims["uid"],
        email=claims.get("email", ""),
        email_verified=claims.get("email_verified", False),
        name=claims.get("name"),
    )


def current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
) -> User:
    user = verify(credentials.credentials)

    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    # Errors from this request name the account by id only, never by email.
    sentry_sdk.set_user({"id": user.uid})

    return user


def optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(optional_bearer)],
) -> User | None:
    """The signed-in user, or None for anonymous visitors and stale tokens on public pages."""
    if credentials is None:
        return None

    return verify(credentials.credentials)


CurrentUser = Annotated[User, Depends(current_user)]
OptionalUser = Annotated[User | None, Depends(optional_user)]
