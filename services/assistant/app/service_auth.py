from prepza_common.service_auth import callee_secret, issue_token

SERVICE_NAME = "assistant"


def service_token(callee: str) -> str:
    """A token for calling `callee`, signed with that service's key. Companies reads it in the
    X-Assistant header, to audit the reads made through the assistant as such."""
    return issue_token(SERVICE_NAME, callee, callee_secret(callee))
