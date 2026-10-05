from enum import StrEnum

from prepza_common.constants import DEFAULT_QUESTION_SECONDS  # noqa: F401 (re-exported)


class InterviewStatus(StrEnum):
    """Where a test stands, as its lists show it (helpers/interviews.py decides)."""

    # No candidate invited yet.
    NEW = "new"
    # Candidates invited.
    IN_PROCESS = "in_process"
    # The company marked it as hired.
    HIRED = "hired"


# Timed interviews: the seconds each question starts with, and the range an admin can set.
MIN_QUESTION_SECONDS = 10
MAX_QUESTION_SECONDS = 600
# The grade, in percent, a finished candidate needs to pass, and the range a company can set.
DEFAULT_PASS_MARK = 70
MIN_PASS_MARK = 1
MAX_PASS_MARK = 100
# Questions each candidate gets from a topic until a manager sets another number: a short
# interview, drawn at random from the topic's whole bank.
DEFAULT_TOPIC_QUESTIONS = 10
