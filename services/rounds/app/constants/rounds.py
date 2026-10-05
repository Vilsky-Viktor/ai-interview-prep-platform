from enum import StrEnum


class RoundStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


OPTIONS_PER_QUESTION = 4
# Score of one answer: every question is multiple choice, so it's right or wrong.
CORRECT_SCORE = 100

# The help chat couldn't answer; its replies are short, so a call silent for longer has hung.
CHAT_FAILED = "Couldn't get a reply right now. Please try again."
CHAT_TIMEOUT_SECONDS = 60

# A timed interview's question ran out of time; it counts as wrong.
TIME_UP = "Time is up for this question."
# Extra seconds an answer may arrive after the deadline, for the trip to the server.
TIME_GRACE_SECONDS = 2
# A candidate's whole interview expires at its start plus every question's time and this share
# more; then it finishes by itself, as if the candidate had finished it.
INTERVIEW_TIME_MARGIN = 0.1
# Expired interviews finished per scheduled run; the next run takes the rest.
EXPIRY_BATCH = 100
