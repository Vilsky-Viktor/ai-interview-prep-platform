EVENTS_STREAM = "events"
# Roughly this many recent events are kept; older ones are trimmed as new ones arrive.
EVENTS_MAX_LENGTH = 10_000
CANDIDATE_INVITED = "candidate.invited"
# A company interview's questions are saved; the event carries the set and its title.
GENERATION_COMPLETED = "generation.completed"
# Generation cancelled an interview's topic review that waited too long; the interview goes too.
GENERATION_CANCELLED = "generation.cancelled"

CONSUMER_GROUP = "companies"
READ_COUNT = 10
READ_BLOCK_MS = 5000
# Must be longer than the blocking read, or every idle read times out.
READ_SOCKET_TIMEOUT_S = 15
# Events left pending by a failure are picked up again after this long.
RECLAIM_IDLE_MS = 60_000
RECLAIM_INTERVAL_S = 60
# After an error (Redis restarting, say), the listener waits this long and starts again.
RESTART_DELAY_S = 5
