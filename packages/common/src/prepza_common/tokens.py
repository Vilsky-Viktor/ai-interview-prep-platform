import hashlib
import secrets


def hashed(token: str) -> str:
    """What's stored of a secret token (an API key, an AI app's access): its SHA-256, so a
    leaked database gives no working tokens."""
    return hashlib.sha256(token.encode()).hexdigest()


def new_token(prefix: str, size: int) -> tuple[str, str]:
    """A new random token, `prefix` and `size` random bytes in URL-safe characters, and its
    hash."""
    token = prefix + secrets.token_urlsafe(size)

    return token, hashed(token)
