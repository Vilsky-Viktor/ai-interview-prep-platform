from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth

from app.schemas.user import User

bearer = HTTPBearer()
optional_bearer = HTTPBearer(auto_error=False)


def verify(token: str) -> User | None:
    try:
        claims = firebase_auth.verify_id_token(token)
    except (ValueError, firebase_auth.InvalidIdTokenError):
        return None

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
