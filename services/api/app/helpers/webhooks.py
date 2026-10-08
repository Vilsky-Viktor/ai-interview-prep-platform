import hashlib
import hmac
import ipaddress
import json
import secrets
import socket
from urllib.parse import urlsplit


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
    web hook can't reach prepza's own services or the cloud's metadata server."""
    parts = urlsplit(url)

    if parts.scheme != "https" or not parts.hostname:
        return False

    try:
        found = socket.getaddrinfo(parts.hostname, parts.port or 443, proto=socket.IPPROTO_TCP)
    except (socket.gaierror, UnicodeError):
        return False

    return all(ipaddress.ip_address(item[4][0]).is_global for item in found)
