from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth

from app.schemas.user import User

bearer = HTTPBearer()


def current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
) -> User:
    try:
        claims = firebase_auth.verify_id_token(credentials.credentials)
    except (ValueError, firebase_auth.InvalidIdTokenError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    return User(
        uid=claims["uid"],
        email=claims.get("email", ""),
        email_verified=claims.get("email_verified", False),
        name=claims.get("name"),
    )


CurrentUser = Annotated[User, Depends(current_user)]
