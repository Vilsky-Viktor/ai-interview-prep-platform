import hashlib
import hmac


def signature_valid(header: str, body: bytes, secret: str, now: float, tolerance: int) -> bool:
    """Checks Paddle's `Paddle-Signature: ts=...;h1=...`: an HMAC-SHA256 of "ts:body" with the
    webhook secret, made within `tolerance` seconds."""
    if not secret:
        return False

    parts = dict(part.split("=", 1) for part in header.split(";") if "=" in part)
    timestamp, received = parts.get("ts", ""), parts.get("h1", "")

    if not timestamp.isdigit() or abs(now - int(timestamp)) > tolerance:
        return False

    expected = hmac.new(
        secret.encode(), f"{timestamp}:".encode() + body, hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, received)
