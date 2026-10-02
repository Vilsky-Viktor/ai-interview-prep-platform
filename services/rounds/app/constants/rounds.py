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
