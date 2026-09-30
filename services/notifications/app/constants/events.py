EVENTS_STREAM = "events"
CONSUMER_GROUP = "notifications"
# Delivery attempts per event, and where events go once they run out.
ATTEMPTS_KEY = "events:notifications:attempts"
DEAD_LETTER_STREAM = "events:notifications:dead"
DEAD_LETTER_MAX_LENGTH = 10_000

PREPARATION_SHARED = "preparation.shared"
CANDIDATE_INVITED = "candidate.invited"

READ_COUNT = 10
READ_BLOCK_MS = 5000
# Must be longer than the blocking read, or every idle read times out.
READ_SOCKET_TIMEOUT_S = 15
# Failed events stay pending; ones idle this long are picked up and tried again.
RECLAIM_IDLE_MS = 60_000
RECLAIM_INTERVAL_S = 60
MAX_ATTEMPTS = 5
