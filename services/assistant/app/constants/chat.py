from enum import StrEnum


class Role(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class Source(StrEnum):
    TEXT = "text"
    VOICE = "voice"


class Status(StrEnum):
    COMPLETE = "complete"
    # Stopped by the user (or a closed tab), with the text it had so far.
    CANCELLED = "cancelled"
    FAILED = "failed"


class ToolState(StrEnum):
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


# A message the user sends, and the page they're on (context for the model only).
MAX_MESSAGE_LENGTH = 2_000
MAX_PAGE_LENGTH = 200
# A conversation's title: the start of its first message.
TITLE_LENGTH = 80

# The model: one call's longest answer, how long it may take and how often it's retried.
MAX_ANSWER_TOKENS = 1_500
MODEL_TIMEOUT_SECONDS = 60
MODEL_RETRIES = 2
# Steps that call tools in one turn; after the last, the model must answer with what it has.
MAX_TOOL_STEPS = 6
# A whole turn, tools included.
TURN_SECONDS = 90
# A comment goes out after this long without an event, so proxies keep the stream open.
KEEP_ALIVE_SECONDS = 15
# The earlier messages the model reads with a new one: the latest this many, within this many
# characters (their tool results included while they fit).
HISTORY_MESSAGES = 20
HISTORY_CHARACTERS = 24_000

# What the user reads; translated by its English text.
CHAT_FAILED = "Couldn't get a reply right now. Please try again."
SESSION_EXPIRED = "Your session expired. Sign in again."
QUESTION_TOO_LONG = "The question is too long."
NOT_FOUND = "Not found"
COMPANY_NOT_FOUND = "Company not found"
# The error event's code when a service refused the user's token mid-turn: the panel refreshes
# the token and sends the message again, once.
SESSION_EXPIRED_CODE = "session_expired"
