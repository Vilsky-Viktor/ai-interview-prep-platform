from datetime import UTC, datetime, timedelta

import jwt

from app.config.settings import settings

SERVICE_NAME = "companies"
TOKEN_LIFETIME = timedelta(seconds=60)


def service_token() -> str:
    now = datetime.now(UTC)
    claims = {"iss": SERVICE_NAME, "iat": now, "exp": now + TOKEN_LIFETIME}

    return jwt.encode(claims, settings.service_secret, algorithm="HS256")
