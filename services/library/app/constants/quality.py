from enum import StrEnum


class QualityFlag(StrEnum):
    # The option marked correct looks wrong.
    WRONG_KEY = "wrong_key"
    # Unclear, off topic, disliked, or answered right far less often than by chance.
    REWRITE = "rewrite"
    # A wrong option almost nobody picks, or a question almost everybody gets right.
    WEAK_OPTIONS = "weak_options"


# Answer statistics say nothing before this many answers.
MIN_ANSWERS = 30
TOO_HARD_RATE = 0.15
TOO_EASY_RATE = 0.95
# A wrong option picked by a smaller share of answers adds nothing.
DEAD_OPTION_SHARE = 0.02
# Reports of one reason that flag a question.
REPORTS_TO_FLAG = 2
# Thumbs down that flag a question, when they're also at least twice its thumbs up.
DISLIKES_TO_FLAG = 3
