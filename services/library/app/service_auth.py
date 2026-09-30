from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config.settings import settings

bearer = HTTPBearer()


def verify_service(credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)]) -> str:
    """Accepts only short-lived tokens signed by another prepza service; returns its name."""
    try:
        claims = jwt.decode(
            credentials.credentials,
            settings.service_secret,
            algorithms=["HS256"],
            options={"require": ["exp", "iss"]},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid service token")

    return claims["iss"]


ServiceCaller = Annotated[str, Depends(verify_service)]
