from urllib.parse import urlparse

from app.constants.mcp import (
    KNOWN_CLIENTS,
    LOCAL_APP,
    LOOPBACK_HOSTS,
    MAX_CLIENT_NAME_LENGTH,
    REFUSED_REDIRECT_SCHEMES,
)


def describe_client(reported_name: str | None, redirect_uri: str) -> tuple[str, str, bool]:
    """What the consent page names an app by: (its name, the site it returns to, whether prepza
    knows it). A known site names the app, whatever it calls itself; an app on the user's own
    computer is named as it says; any other is unknown, and its name is only what it says. Only
    an https address is a known site (javascript://claude.ai/ isn't Claude); names are cut to
    what a connection keeps."""
    url = urlparse(redirect_uri)
    host = (url.hostname or "").lower()
    reported = (reported_name or "").strip()[:MAX_CLIENT_NAME_LENGTH]

    if url.scheme == "https" and host in KNOWN_CLIENTS:
        return KNOWN_CLIENTS[host], host, True

    if url.scheme in ("http", "https") and host in LOOPBACK_HOSTS:
        return reported or LOCAL_APP, host, True

    return reported or host[:MAX_CLIENT_NAME_LENGTH], host, False


def refused_redirect(redirect_uri: str) -> bool:
    """A return address that would run or read something in the browser instead of opening an
    app (constants/mcp.py REFUSED_REDIRECT_SCHEMES)."""
    return urlparse(redirect_uri).scheme.lower() in REFUSED_REDIRECT_SCHEMES
