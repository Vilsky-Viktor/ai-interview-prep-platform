from cryptography.fernet import Fernet, InvalidToken


def encrypt(key: str, text: str) -> str:
    """`text` encrypted with `key` (a Fernet key, like ATS_ENCRYPTION_KEY or SLACK_ENCRYPTION_KEY)."""
    return Fernet(key).encrypt(text.encode()).decode()


def decrypt(key: str, token: str) -> str | None:
    """What `encrypt` sealed, or None when it was sealed with another key or changed, or the key
    is missing or isn't a Fernet key."""
    try:
        return Fernet(key).decrypt(token.encode()).decode()
    except (InvalidToken, ValueError):
        return None
