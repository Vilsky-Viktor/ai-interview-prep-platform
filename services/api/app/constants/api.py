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
# Requests per company per minute, all its keys together.
REQUESTS_PER_MINUTE = 60
# How long a key maker's access (still an owner or admin?) is trusted before companies is asked
# again, in this instance's memory.
ACCESS_CACHE_SECONDS = 60
# A key's "last used" is written at most this often.
LAST_USED_EVERY = timedelta(minutes=1)
# How long a web hook's endpoint may take to answer, its whole answer included.
WEBHOOK_TIMEOUT_SECONDS = 10
# The header that carries a web hook's signature: t=<unix seconds>,v1=<hex HMAC-SHA256>.
SIGNATURE_HEADER = "Prepza-Signature"
# How long a web hook's deliveries are remembered: past Pub/Sub's redelivery of an event.
DELIVERIES_KEPT = timedelta(days=30)
# An event a web hook didn't take is sent again by the retry job (every 5 minutes): first after
# RETRY_FIRST_DELAY, then twice as long each time, at most RETRY_MAX_DELAY apart. After
# RETRY_GIVE_UP it's dropped, and the web hook is paused (`failing`): it gets no events, and its
# other retries go, until a test event goes through.
RETRY_FIRST_DELAY = timedelta(minutes=5)
RETRY_MAX_DELAY = timedelta(hours=6)
RETRY_GIVE_UP = timedelta(days=3)
# The retry job sends RETRY_BATCH events at once, batch after batch, and starts none
# RETRY_RUN_SECONDS into its run, so it ends within its 60 seconds (each send has
# WEBHOOK_TIMEOUT_SECONDS); the rest wait for the next run.
RETRY_BATCH = 25
RETRY_RUN_SECONDS = 40
# A run that was cut off leaves its events to be sent again after this long.
RETRY_LEASE = timedelta(minutes=10)
# Where a candidate's results are in prepza.
CANDIDATE_LINK = "{site}/companies/{company_id}/interviews/{interview_id}/candidates/{invite_id}"
# The candidate's own invite link, to send them yourself.
INVITE_LINK = "{site}/invite/{token}"

# The API page, as a notification opens it.
API_PAGE = "/companies/{company_id}/integrations/api"

# Each web hook's delivery log keeps its latest sends.
WEBHOOK_LOG_KEPT = 20

# A POST with an Idempotency-Key gives the same result for that key this long (a client's retry
# doesn't invite or create twice); a retry while the first request still runs is refused.
IDEMPOTENCY_SECONDS = 24 * 60 * 60
IDEMPOTENCY_IN_PROGRESS = "A request with this Idempotency-Key is still running. Try again shortly."
