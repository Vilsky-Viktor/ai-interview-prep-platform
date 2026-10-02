from enum import StrEnum


class RoundStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class ChatRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


MAX_CHAT_MESSAGE_LENGTH = 2_000
OPTIONS_PER_QUESTION = 4
# Score of one answer: every question is multiple choice, so it's right or wrong.
CORRECT_SCORE = 100
# A certificate needs every question of the topic answered, the latest answers at least this
# percent correct.
CERTIFICATE_MIN_SCORE = 70

CHAT_FAILED = "Couldn't get a reply right now. Please try again."
# Chat replies are short; a call silent for longer has hung.
CHAT_TIMEOUT_SECONDS = 60
# Earlier chat messages sent with a new one. The system prompt already holds the question, the
# correct option and the learner's pick, so older turns add little but cost.
CHAT_HISTORY_MESSAGES = 10

# A timed interview's question ran out of time; it counts as wrong.
TIME_UP = "Time is up for this question."
# Extra seconds an answer may arrive after the deadline, for the trip to the server.
TIME_GRACE_SECONDS = 2

# Shown to learners before they practice; the pass mark comes from CERTIFICATE_MIN_SCORE.
CERTIFICATE_RULES = [
    "Answer every question of the topic.",
    "Only your latest answer to each question counts.",
    f"At least {CERTIFICATE_MIN_SCORE}% of your answers must be correct.",
    "Once all of the above are done, you'll receive your certificate.",
]
