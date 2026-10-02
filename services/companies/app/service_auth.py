from prepza_common.service_auth import issue_token

from app.config.settings import settings

SERVICE_NAME = "companies"


def service_token() -> str:
    return issue_token(SERVICE_NAME, settings.service_secret)
