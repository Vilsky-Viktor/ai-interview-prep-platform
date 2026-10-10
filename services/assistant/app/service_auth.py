from prepza_common.service_auth import callee_secret, issue_token, service_caller

from app.config.settings import settings

SERVICE_NAME = "assistant"


def service_token(callee: str, issuer: str = SERVICE_NAME) -> str:
    """A token for calling `callee`, signed with that service's key. Companies reads it in the
    X-Assistant header, to audit the reads made through the assistant (or, issued as "mcp",
    through an AI app) as such."""
    return issue_token(issuer, callee, callee_secret(callee))


# Calls to this service (library deleting or exporting a user's data), signed with its own key.
ServiceCaller = service_caller(settings.service_secret, SERVICE_NAME)
