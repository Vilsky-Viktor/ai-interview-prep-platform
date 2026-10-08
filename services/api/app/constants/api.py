from datetime import timedelta
from enum import StrEnum

# An API key: this prefix and random characters; the list shows the key's first characters.
KEY_PREFIX = "pz_"
KEY_BYTES = 30
KEY_SHOWN = 10


# When a new key expires, as the API page offers it: in a number of months, or never.
class KeyExpiry(StrEnum):
    MONTH = "1"
    MONTHS_3 = "3"
    MONTHS_6 = "6"
    MONTHS_12 = "12"
    NEVER = "never"


KEY_EXPIRY_MONTHS = {
    KeyExpiry.MONTH: 1,
    KeyExpiry.MONTHS_3: 3,
    KeyExpiry.MONTHS_6: 6,
    KeyExpiry.MONTHS_12: 12,
    KeyExpiry.NEVER: None,
}
# Keys and web hooks a company may have at once.
MAX_KEYS = 10
MAX_WEBHOOKS = 5
MAX_NAME_LENGTH = 80
MAX_URL_LENGTH = 500
# Requests per key per minute.
REQUESTS_PER_MINUTE = 60
MINUTE_SECONDS = 60
# A key's "last used" is written at most this often.
LAST_USED_EVERY = timedelta(minutes=1)
# How long a web hook's endpoint may take to answer.
WEBHOOK_TIMEOUT_SECONDS = 10
# The header that carries a web hook's signature: t=<unix seconds>,v1=<hex HMAC-SHA256>.
SIGNATURE_HEADER = "Prepza-Signature"
# How long a web hook's deliveries are remembered: past Pub/Sub's redelivery of an event.
DELIVERIES_KEPT = timedelta(days=30)
# Where a candidate's results are in prepza.
CANDIDATE_LINK = "{site}/companies/{company_id}/interviews/{interview_id}/candidates/{invite_id}"
