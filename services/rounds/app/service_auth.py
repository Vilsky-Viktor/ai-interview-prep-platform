from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config.settings import settings

SERVICE_NAME = "rounds"
TOKEN_LIFETIME = timedelta(seconds=60)
bearer = HTTPBearer()


def service_token() -> str:
    now = datetime.now(UTC)
    claims = {"iss": SERVICE_NAME, "iat": now, "exp": now + TOKEN_LIFETIME}

    return jwt.encode(claims, settings.service_secret, algorithm="HS256")


def verify_service(credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)]) -> str:
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
