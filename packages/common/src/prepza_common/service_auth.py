import os
from datetime import UTC, datetime
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from prepza_common.constants import SERVICE_TOKEN_LIFETIME

bearer = HTTPBearer()


def callee_secret(callee: str) -> str:
    """The key of the service being called: each service has its own, and a caller holds only
    the keys of services it calls (<CALLEE>_SERVICE_SECRET, e.g. LIBRARY_SERVICE_SECRET)."""
    return os.environ[f"{callee.upper()}_SERVICE_SECRET"]


def issue_token(caller: str, callee: str, secret: str) -> str:
    """A short-lived token from `caller`, usable only at `callee`, signed with `callee`'s key."""
    now = datetime.now(UTC)
    claims = {"iss": caller, "aud": callee, "iat": now, "exp": now + SERVICE_TOKEN_LIFETIME}

    return jwt.encode(claims, secret, algorithm="HS256")


def service_caller(secret: str, name: str):
    """A FastAPI parameter type that admits only tokens addressed to service `name` and signed
    with its key; it holds the calling service's name."""

    def verify_service(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
    ) -> str:
        try:
            claims = jwt.decode(
                credentials.credentials,
                secret,
                algorithms=["HS256"],
                audience=name,
                options={"require": ["exp", "iss", "aud"]},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid service token")

        return claims["iss"]

    return Annotated[str, Depends(verify_service)]
