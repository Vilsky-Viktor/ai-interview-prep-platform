from prepza_common.service_auth import callee_secret, issue_token, service_caller, token_caller

from app.config.settings import settings
from app.constants.audit import VIAS

SERVICE_NAME = "companies"


def service_token(callee: str) -> str:
    """A token for calling `callee` (library, rounds, ...), signed with that service's key."""
    return issue_token(SERVICE_NAME, callee, callee_secret(callee))


# Calls to this service, signed with its own key.
ServiceCaller = service_caller(settings.service_secret, SERVICE_NAME)


def via_of(token: str | None) -> str | None:
    """What a user's request came through, when not the app itself: the in-app assistant
    ("assistant") or an AI app connected over MCP ("mcp"), as its X-Assistant header names it in
    a service token the assistant signed for this service. None for a missing or forged one."""
    if not token:
        return None

    caller = token_caller(token, settings.service_secret, SERVICE_NAME)

    return caller if caller in VIAS else None
