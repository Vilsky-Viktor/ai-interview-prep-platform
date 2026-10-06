import hashlib

from app.constants.gifts import DOTLESS_DOMAINS, GMAIL


def inbox_of(email: str) -> str:
    """The inbox an address delivers to: case, a "+tag" and Gmail's dots don't make another
    person, so they can't claim a welcome gift twice."""
    local, _, domain = email.strip().lower().rpartition("@")
    local = local.split("+", 1)[0]

    if domain in DOTLESS_DOMAINS:
        local = local.replace(".", "")
        domain = GMAIL

    return f"{local}@{domain}"


def legacy_gift_key(kind: str, email: str) -> str:
    """The key gifts had before inbox_of: the plain lowercased email. Still checked, so an owner
    who got a gift then can't get it again under the new key."""
    digest = hashlib.sha256(email.strip().lower().encode()).hexdigest()

    return f"{kind}:{digest}"


def gift_key(kind: str, email: str) -> str:
    """Names a welcome gift by a one-way hash of the inbox: it can be matched again, never read
    back."""
    digest = hashlib.sha256(inbox_of(email).encode()).hexdigest()

    return f"{kind}:{digest}"
