import hashlib


def gift_key(kind: str, email: str) -> str:
    """Names a welcome gift by a one-way hash of the email: it can be matched again, never read
    back."""
    digest = hashlib.sha256(email.strip().lower().encode()).hexdigest()

    return f"{kind}:{digest}"
