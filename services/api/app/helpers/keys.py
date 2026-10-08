import calendar
import hashlib
import secrets
from datetime import datetime

from app.constants.api import KEY_BYTES, KEY_PREFIX, KEY_SHOWN


def hashed(key: str) -> str:
    """What's stored of a key: its SHA-256, so a leaked database gives no working keys."""
    return hashlib.sha256(key.encode()).hexdigest()


def new_key() -> tuple[str, str, str]:
    """A new key, its first characters (to tell keys apart) and its hash."""
    key = KEY_PREFIX + secrets.token_urlsafe(KEY_BYTES)

    return key, key[:KEY_SHOWN], hashed(key)


def expired(expires_at: datetime | None, now: datetime) -> bool:
    """Whether a key with this expiry no longer works; one without never expires."""
    return expires_at is not None and expires_at <= now


def add_months(moment: datetime, months: int) -> datetime:
    """The same day and time `months` later; a day the month doesn't have (Jan 31 + 1) becomes
    its last day."""
    month = moment.month - 1 + months
    year, month = moment.year + month // 12, month % 12 + 1

    return moment.replace(
        year=year, month=month, day=min(moment.day, calendar.monthrange(year, month)[1])
    )
