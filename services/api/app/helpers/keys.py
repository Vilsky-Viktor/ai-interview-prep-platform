import calendar
from datetime import datetime

from prepza_common.tokens import new_token

from app.constants.api import KEY_BYTES, KEY_PREFIX, KEY_SHOWN


def new_key() -> tuple[str, str, str]:
    """A new key, its first characters (to tell keys apart) and its hash."""
    key, key_hash = new_token(KEY_PREFIX, KEY_BYTES)

    return key, key[:KEY_SHOWN], key_hash


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
