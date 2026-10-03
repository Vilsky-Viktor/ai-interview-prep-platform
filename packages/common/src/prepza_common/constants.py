from datetime import timedelta

# Service tokens live this long; each call between services signs a new one.
SERVICE_TOKEN_LIFETIME = timedelta(seconds=60)

HTTP_TIMEOUT_SECONDS = 30
# Retries only connection attempts that failed, so a request is never sent twice.
HTTP_RETRIES = 3

RATE_LIMITED = "Too many requests. Try again later."
SIGN_IN_UNAVAILABLE = "Sign-in is temporarily unavailable. Please try again shortly."
HOUR_SECONDS = 60 * 60
DAY_SECONDS = 24 * HOUR_SECONDS

# Database connections per process: at most DB_POOL_SIZE + DB_MAX_OVERFLOW. Four APIs and the
# generation worker use 50 at most, plus generation's checkpointer pool, under Postgres's default
# 100. Add PgBouncer before replicas would push the total past that.
DB_POOL_SIZE = 5
DB_MAX_OVERFLOW = 5

# Lists are served a page at a time; a page holds at most this many items.
MAX_PAGE_SIZE = 100

# Sentry: share of requests traced for performance, and emails scrubbed from every event.
DEFAULT_TRACES_SAMPLE_RATE = "0.1"
EMAIL_PATTERN = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
REDACTED_EMAIL = "[email]"

# Pub/Sub: the one topic every domain event goes to, and its REST API.
EVENTS_TOPIC = "events"
PUBSUB_URL = "https://pubsub.googleapis.com"
# Google APIs our services call with their own credentials (Pub/Sub, Cloud Tasks).
GOOGLE_SCOPE = "https://www.googleapis.com/auth/cloud-platform"

# Outbox: events published per flush, and how long published ones are kept.
OUTBOX_BATCH = 100
OUTBOX_KEEP_DAYS = 7

# Languages the interface and generated content come in, by code, with the name prompts use.
LANGUAGES = {"en": "English", "ru": "Russian"}
DEFAULT_LANGUAGE = "en"
# The Firebase custom claim that carries the user's language in every ID token.
LANGUAGE_CLAIM = "language"
