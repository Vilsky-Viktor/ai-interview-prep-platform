import hashlib
import hmac
import ipaddress
import json
import secrets
import socket
from datetime import timedelta
from urllib.parse import urlsplit

from app.constants.api import RETRY_FIRST_DELAY, RETRY_MAX_DELAY


def new_secret() -> str:
    """A web hook's signing secret, shown once."""
    return "whsec_" + secrets.token_urlsafe(30)


def body_of(event_id: str, event_type: str, data: dict) -> bytes:
    """What a web hook gets: the event's id (the same on a repeat), its type and data."""
    event = {"id": event_id, "type": event_type, "data": data}

    return json.dumps(event, separators=(",", ":")).encode()


def signature(secret: str, timestamp: int, body: bytes) -> str:
    """The signature header: HMAC-SHA256 of "<timestamp>.<body>" with the web hook's secret."""
    digest = hmac.new(secret.encode(), f"{timestamp}.".encode() + body, hashlib.sha256)

    return f"t={timestamp},v1={digest.hexdigest()}"


def public_address(url: str) -> bool:
    """Whether the URL is HTTPS to a host whose every address is on the public internet, so a
    web hook can't reach prepza's own services or the cloud's metadata server. A lookup that
    fails raises socket.gaierror: it may work on a retry."""
    parts = urlsplit(url)

    if parts.scheme != "https" or not parts.hostname:
        return False

    try:
        found = socket.getaddrinfo(parts.hostname, parts.port or 443, proto=socket.IPPROTO_TCP)
    except UnicodeError:
        return False

    return all(ipaddress.ip_address(item[4][0]).is_global for item in found)


def retry_delay(attempts: int) -> timedelta:
    """How long an event waits to be sent again after its `attempts`-th failed send: twice as
    long each time, from RETRY_FIRST_DELAY up to RETRY_MAX_DELAY."""
    return min(RETRY_FIRST_DELAY * 2 ** (attempts - 1), RETRY_MAX_DELAY)
