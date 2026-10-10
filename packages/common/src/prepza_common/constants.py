from datetime import timedelta

# Service tokens live this long; each call between services signs a new one.
SERVICE_TOKEN_LIFETIME = timedelta(seconds=60)

HTTP_TIMEOUT_SECONDS = 30
# Retries only connection attempts that failed, so a request is never sent twice.
HTTP_RETRIES = 3

RATE_LIMITED = "Too many requests. Try again later."
# Cloud Logging's fields: a JSON log line's `severity` and `message` are read as such, and this
# one ties the line to its request's trace, which the load balancer sends in TRACE_HEADER
# ("TRACE_ID/SPAN_ID;o=1"), so one request can be followed across services.
TRACE_HEADER = "X-Cloud-Trace-Context"
TRACE_FIELD = "logging.googleapis.com/trace"

# Logged when a provider's web hook (Paddle, Resend) fails its signature check: usually a wrong
# secret, so every event is refused. The alert in infra/terraform/monitoring.tf matches it.
WEBHOOK_SIGNATURE_REFUSED = "web hook signature refused"
SIGN_IN_UNAVAILABLE = "Sign-in is temporarily unavailable. Please try again shortly."
HOUR_SECONDS = 60 * 60
DAY_SECONDS = 24 * HOUR_SECONDS

# Database connections per process: at most DB_POOL_SIZE + DB_MAX_OVERFLOW. Services with few,
# short queries pass smaller ones. Every instance's total must fit the database's connection
# budget (infra/terraform/database.tf).
DB_POOL_SIZE = 5
DB_MAX_OVERFLOW = 5
# A pooled connection is replaced once it's this old, instead of pinged before each use (a
# SELECT 1 per checkout). Nothing drops idle ones on the way (Postgres has no idle timeout set,
# and the Cloud SQL connector none); one killed by a database restart fails one request, and
# SQLAlchemy then replaces the whole pool.
DB_POOL_RECYCLE_SECONDS = 1800

# Lists are served a page at a time; a page holds at most this many items.
MAX_PAGE_SIZE = 100

# Who a kept row is by once its user deleted their account (a referral, a generation, an ATS or
# Slack connection, an audit entry): the row stays for its company, without their id.
DELETED_USER = "deleted-user"

# Sentry: share of requests traced for performance, and emails scrubbed from every event.
DEFAULT_TRACES_SAMPLE_RATE = "0.1"
EMAIL_PATTERN = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
REDACTED_EMAIL = "[email]"
# A URL's path, query and user info can carry credentials (a Slack web hook's path, a customer's
# web hook secret, an invite token): only its scheme and host (group 1) reach Sentry, and the
# fields that hold a query alone are dropped.
URL_PATTERN = r"(https?://)(?:[^\s/?#@'\"]*@)?([^\s/?#'\"]+)[^\s'\"]*"
URL_SCRUBBED = r"\1\2"
QUERY_FIELDS = {"query_string", "http.query", "http.fragment"}

# Pub/Sub: the one topic every domain event goes to, and its REST API.
EVENTS_TOPIC = "events"
PUBSUB_URL = "https://pubsub.googleapis.com"
# The attribute that carries an event's own id (its outbox row's), the same on every re-send, so
# consumers can handle it once; events sent without an outbox go without it.
EVENT_ID_ATTRIBUTE = "event_id"
# Publishing from inside a user's request waits at most this long; the scheduled flush sends
# whatever didn't make it.
PUBLISH_IN_REQUEST_TIMEOUT_SECONDS = 5
# Google APIs our services call with their own credentials (Pub/Sub, Cloud Tasks).
GOOGLE_SCOPE = "https://www.googleapis.com/auth/cloud-platform"

# Outbox: events published per call to Pub/Sub, and how long published ones are kept. The
# scheduled flush sends batch after batch until none wait, starting no new batch after
# OUTBOX_FLUSH_SECONDS, so a run (plus its last call's timeout) ends within the shortest
# service timeout (60 s) and a backlog drains in minutes.
OUTBOX_BATCH = 100
OUTBOX_FLUSH_SECONDS = 20
OUTBOX_KEEP_DAYS = 7
# Pub/Sub's answers that mean it won't take a message (too large or malformed): the event is
# tried alone, and parked after OUTBOX_MAX_ATTEMPTS of them so it can't hold up the others.
# Outages and other errors count against no event; the events wait for the next flush.
OUTBOX_REJECTED_STATUSES = (400, 413)
OUTBOX_MAX_ATTEMPTS = 5

# Languages the interface and generated content come in, by code, with the name prompts use.
# Every language prepza supports: the interface, its messages and emails, and the tests it
# generates. Names are as prompts use them.
LANGUAGES = {
    "en": "English",
    "ru": "Russian",
    "uk": "Ukrainian",
    "es": "Spanish",
    "pt": "Portuguese (Brazil)",
    "de": "German",
    "fr": "French",
    "it": "Italian",
    "pl": "Polish",
    "nl": "Dutch",
    "tr": "Turkish",
    "ar": "Arabic",
    "he": "Hebrew",
    "fa": "Persian",
    "ja": "Japanese",
    "zh": "Chinese (Simplified)",
    "ko": "Korean",
    "hi": "Hindi",
    "id": "Indonesian",
    "th": "Thai",
    "vi": "Vietnamese",
    "fil": "Filipino",
    "et": "Estonian",
}
# How hard a test is, from its requirements; generation decides it and
# library filters by it.
LEVELS = ("basic", "medium", "hard")
# Of those, the ones written right to left.
RTL_LANGUAGES = {"ar", "he", "fa"}
DEFAULT_LANGUAGE = "en"
# The Firebase custom claim that carries the user's language in every ID token.
LANGUAGE_CLAIM = "language"

# Limits a service enforces and the help chat explains, so both read the same numbers.
# Companies one person may own; the welcome credits come with the first one only (companies).
MAX_OWNED_COMPANIES = 3
# Interviews are free to generate, so each company may start this many a day (companies).
INTERVIEWS_PER_DAY = 10
# $1 buys this many credits (billing sells them; the FAQ shows prices in dollars too).
CREDITS_PER_DOLLAR = 100
# Generating an interview is free and paid for by its candidates: a company can have only this many
# interviews waiting without one before it generates another.
MAX_INTERVIEWS_WITHOUT_CANDIDATES = 3
# Seconds each timed interview question starts with; an admin can change it (companies).
DEFAULT_QUESTION_SECONDS = 60

# Funnel events for analytics go on the events topic with this type prefix; only they reach
# BigQuery, and the services' push subscriptions leave them out.
FUNNEL_PREFIX = "funnel."

# Holds the referral code from a ?ref= link until the new person signs up or makes a company.
REFERRAL_COOKIE = "prepza_ref"

# A test's title, as its company can rename it; generated titles aim for 60.
MAX_TITLE_LENGTH = 70
# The longest candidate name kept (from a sign-in, an inviter or an ATS); a longer one is cut.
MAX_CANDIDATE_NAME_LENGTH = 200

# A job description, as pasted to generate a test.
MAX_GOAL_LENGTH = 10_000

# A news post's title and text (library), written in English and translated into each language
# (generation); a translation must fit them too.
MAX_NEWS_TITLE_LENGTH = 120
MAX_NEWS_TEXT_LENGTH = 500

# The emergency pause (pause.py): one Redis key every service reads, and the message it refuses
# with while it's on.
PAUSE_KEY = "pause:on"
PAUSED = "New interviews and AI features are paused for now. Please try again later."

# Maintenance mode (maintenance.py): one Redis key every service reads, the message every refused
# request gets while it's on, and what stays open: health checks, the switch itself, calls
# between services, Pub/Sub and Scheduler pushes (under /internal/) and Paddle's and Resend's
# webhooks, so no event, job or payment is lost.
MAINTENANCE_KEY = "maintenance:on"
MAINTENANCE = "prepza is under maintenance. We'll be back soon."
MAINTENANCE_OPEN_PATHS = {"/health", "/ready", "/maintenance", "/superadmin/maintenance"}
MAINTENANCE_OPEN_PREFIXES = ("/internal/", "/webhooks/")
# Each instance reads the switch at most this often; turning it takes that long to reach them all.
MAINTENANCE_CACHE_SECONDS = 5
