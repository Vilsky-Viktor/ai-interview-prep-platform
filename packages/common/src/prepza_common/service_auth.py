from datetime import UTC, datetime
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from prepza_common.constants import SERVICE_TOKEN_LIFETIME

bearer = HTTPBearer()


def issue_token(service_name: str, secret: str) -> str:
    """A short-lived token another prepza service accepts from `service_name`."""
    now = datetime.now(UTC)
    claims = {"iss": service_name, "iat": now, "exp": now + SERVICE_TOKEN_LIFETIME}

    return jwt.encode(claims, secret, algorithm="HS256")


def service_caller(secret: str):
    """A FastAPI parameter type that admits only tokens signed with `secret`; it holds the
    calling service's name."""

    def verify_service(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
    ) -> str:
        try:
            claims = jwt.decode(
                credentials.credentials,
                secret,
                algorithms=["HS256"],
                options={"require": ["exp", "iss"]},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid service token")

        return claims["iss"]

    return Annotated[str, Depends(verify_service)]
