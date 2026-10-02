from enum import StrEnum


class IntegritySignal(StrEnum):
    """What the candidate's browser reports during an interview."""

    TAB_LEAVE = "tab_leave"
    COPY = "copy"


# Answers faster than this are too quick to have read the question; the scorecard flags them.
FAST_ANSWER_SECONDS = 3
