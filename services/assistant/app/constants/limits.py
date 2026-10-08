# How much the assistant may be used; over a limit, a 429 before anything runs. Messages are
# counted as they're sent; spending in tokens (input and output, every model call of a turn),
# added after each turn, so a turn already started always finishes.

MESSAGES_PER_USER_HOUR = 30
MESSAGES_PER_USER_DAY = 200
# One company's members together, and everyone.
MESSAGES_PER_COMPANY_DAY = 1_000
MESSAGES_PER_DAY = 20_000

# A turn reading the platform guide uses about 30,000 tokens; most use a few thousand.
TOKENS_PER_USER_DAY = 2_000_000
TOKENS_PER_COMPANY_DAY = 6_000_000
TOKENS_PER_DAY = 200_000_000

# The longest voice message (the panel stops recording then).
MAX_AUDIO_SECONDS = 60
# Voice messages a user may have transcribed in an hour (each also counts as a message once sent;
# this one counts the ones too short or silent to send as well).
TRANSCRIPTIONS_PER_USER_HOUR = 60
