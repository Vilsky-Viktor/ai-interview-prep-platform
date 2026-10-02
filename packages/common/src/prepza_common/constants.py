from datetime import timedelta

# Service tokens live this long; each call between services signs a new one.
SERVICE_TOKEN_LIFETIME = timedelta(seconds=60)

HTTP_TIMEOUT_SECONDS = 30
# Retries only connection attempts that failed, so a request is never sent twice.
HTTP_RETRIES = 3

RATE_LIMITED = "Too many requests. Try again later."

# Database connections per process: at most DB_POOL_SIZE + DB_MAX_OVERFLOW. Four APIs and the
# generation worker use 50 at most, plus generation's checkpointer pool, under Postgres's default
# 100. Add PgBouncer before replicas would push the total past that.
DB_POOL_SIZE = 5
DB_MAX_OVERFLOW = 5

# Lists are served a page at a time; a page holds at most this many items.
MAX_PAGE_SIZE = 100
