from enum import StrEnum


class HelpRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


# Legal documents the help routes serve, by the path they're asked for under.
class LegalDocument(StrEnum):
    TERMS = "terms"
    PRIVACY = "privacy"


# The page keeps the conversation and sends it whole; nothing of it is stored. A new question's
# length, the bounds on what's sent, and the earlier messages the model sees with a question.
MAX_HELP_QUESTION_LENGTH = 1_000
MAX_HELP_MESSAGE_LENGTH = 10_000
MAX_HELP_MESSAGES = 200
HELP_HISTORY_MESSAGES = 10
LAST_NOT_QUESTION = "The conversation must end with a question."
QUESTION_TOO_LONG = "The question is too long."
