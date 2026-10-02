EVENTS_STREAM = "events"
# Roughly this many recent events are kept; older ones are trimmed as new ones arrive.
EVENTS_MAX_LENGTH = 10_000
# A company interview's questions are saved; companies stores the set and its title.
GENERATION_COMPLETED = "generation.completed"
# An interview generation was cancelled by the system; companies removes the interview.
GENERATION_CANCELLED = "generation.cancelled"
