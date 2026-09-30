from enum import StrEnum


class Mode(StrEnum):
    OPEN = "open"
    CHOICE = "choice"


class RoundStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class ChatRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


MAX_ANSWER_LENGTH = 5_000
MAX_CHAT_MESSAGE_LENGTH = 2_000
OPTIONS_PER_QUESTION = 4
# A certificate needs every topic question answered across open answer rounds, averaging at least this.
CERTIFICATE_MIN_SCORE = 70

GRADING_FAILED = "Couldn't grade your answer right now. Please try again."
CHAT_FAILED = "Couldn't get a reply right now. Please try again."
