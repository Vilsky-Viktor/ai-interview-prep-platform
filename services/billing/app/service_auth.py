from prepza_common.service_auth import issue_token, service_caller

from app.config.settings import settings

SERVICE_NAME = "billing"


def service_token() -> str:
    return issue_token(SERVICE_NAME, settings.service_secret)


ServiceCaller = service_caller(settings.service_secret)
