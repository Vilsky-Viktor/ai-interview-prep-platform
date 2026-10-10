from urllib.parse import urlparse

from app.constants.mcp import KNOWN_CLIENTS, LOCAL_APP, LOOPBACK_HOSTS, MAX_CLIENT_NAME_LENGTH


def describe_client(reported_name: str | None, redirect_uri: str) -> tuple[str, str, bool]:
    """What the consent page names an app by: (its name, the site it returns to, whether prepza
    knows it). A known site names the app, whatever it calls itself; an app on the user's own
    computer is named as it says; any other is unknown, and its name is only what it says."""
    host = (urlparse(redirect_uri).hostname or "").lower()
    reported = (reported_name or "").strip()[:MAX_CLIENT_NAME_LENGTH]

    if host in KNOWN_CLIENTS:
        return KNOWN_CLIENTS[host], host, True

    if host in LOOPBACK_HOSTS:
        return reported or LOCAL_APP, host, True

    return reported or host, host, False
