from prepza_common.constants import DEFAULT_QUESTION_SECONDS  # noqa: F401 (re-exported)

# Timed interviews: the seconds each question starts with, and the range an admin can set.
MIN_QUESTION_SECONDS = 10
MAX_QUESTION_SECONDS = 600
# Questions each candidate gets from a topic until a manager sets another number: a short
# interview, drawn at random from the topic's whole bank.
DEFAULT_TOPIC_QUESTIONS = 10
