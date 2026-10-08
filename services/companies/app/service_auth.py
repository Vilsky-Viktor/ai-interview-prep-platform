from prepza_common.service_auth import callee_secret, issue_token, service_caller, token_caller

from app.config.settings import settings
from app.constants.audit import VIA_ASSISTANT

SERVICE_NAME = "companies"


def service_token(callee: str) -> str:
    """A token for calling `callee` (library, rounds, ...), signed with that service's key."""
    return issue_token(SERVICE_NAME, callee, callee_secret(callee))


# Calls to this service, signed with its own key.
ServiceCaller = service_caller(settings.service_secret, SERVICE_NAME)


def from_assistant(token: str | None) -> bool:
    """Whether a user's request came through the in-app assistant: its X-Assistant header holds
    a service token the assistant signed for this service. A missing or forged one isn't."""
    if not token:
        return False

    return token_caller(token, settings.service_secret, SERVICE_NAME) == VIA_ASSISTANT
