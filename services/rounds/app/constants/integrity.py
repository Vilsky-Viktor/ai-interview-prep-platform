from enum import StrEnum


class IntegritySignal(StrEnum):
    """What the candidate's browser reports during an interview."""

    TAB_LEAVE = "tab_leave"
    COPY = "copy"


# Answers faster than this are too quick to have read the question; the scorecard flags them.
FAST_ANSWER_SECONDS = 3

# What one session's browser may report: this many a minute, and at most this many per question
# kept (one already flags the candidate, more say nothing new), so a script can't flood the
# table or the scorecard that loads them.
SIGNALS_PER_MINUTE = 60
SIGNALS_WINDOW_SECONDS = 60
MAX_SIGNALS_PER_QUESTION = 50
