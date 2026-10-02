import os
from functools import cache

import google.auth
from fastapi import Depends, HTTPException, Request, status
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import id_token
from prepza_common.constants import GOOGLE_SCOPE


def project() -> str:
    return os.environ["GOOGLE_CLOUD_PROJECT"]


def running_locally() -> bool:
    """Local development uses a demo- project, as the Firebase emulator requires: no Google
    Cloud, and emulators or direct calls instead of Pub/Sub, Cloud Tasks and Cloud Scheduler."""
    return project().startswith("demo-")


@cache
def credentials():
    found, _ = google.auth.default(scopes=[GOOGLE_SCOPE])

    return found


def access_token() -> str:
    """The service's own Google token (Cloud Run's service account); refreshed when stale."""
    current = credentials()

    if not current.valid:
        current.refresh(GoogleRequest())

    return current.token


def verify_invoker(request: Request) -> None:
    """Admits only Google's calls on our behalf: Pub/Sub pushes, Cloud Tasks and Cloud
    Scheduler, all signed as the invoker service account for this service's address
    (INVOKER_SERVICE_ACCOUNT, INVOKER_AUDIENCE). Locally nothing signs, so nothing is checked."""
    if running_locally():
        return

    token = request.headers.get("Authorization", "").removeprefix("Bearer ")

    try:
        claims = id_token.verify_oauth2_token(
            token, GoogleRequest(), os.environ["INVOKER_AUDIENCE"]
        )
    except (ValueError, KeyError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid invoker token")

    if not claims.get("email_verified") or claims.get("email") != os.getenv(
        "INVOKER_SERVICE_ACCOUNT"
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not the invoker service account")


Invoker = Depends(verify_invoker)
