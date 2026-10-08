from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from prepza_common.auth import bearer, current_user
from prepza_common.user import User


def user_with_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
) -> tuple[User, str]:
    """The signed-in user and their raw Firebase token, which the assistant's tools send on to
    the other services as the user. The token stays in memory: never stored, logged or shown to
    the model."""
    return current_user(credentials), credentials.credentials


UserWithToken = Annotated[tuple[User, str], Depends(user_with_token)]
