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
# What a paid turn needs available; billing charges it.
CHAT_TURN_CREDITS = 1
# New topics of other people's public kits a learner may start a day (UTC); continuing a topic
# already started is never limited.
PUBLIC_TOPICS_PER_DAY = 3
PUBLIC_TOPICS_LIMIT = (
    "You've started 3 new public topics today. Come back tomorrow, or generate your own kit now."
)
NOT_ENOUGH_CREDITS = "Not enough credits. Top up to continue."

# Earlier chat messages sent with a new one. The system prompt already holds the question, the
# correct option and the learner's pick, so older turns add little but cost.
CHAT_HISTORY_MESSAGES = 10

# A timed interview's question ran out of time; it counts as wrong.
TIME_UP = "Time is up for this question."
# Extra seconds an answer may arrive after the deadline, for the trip to the server.
TIME_GRACE_SECONDS = 2
# A candidate's whole interview expires at its start plus every question's time and this share
# more; then it finishes by itself, as if the candidate had finished it.
INTERVIEW_TIME_MARGIN = 0.1
# Expired interviews finished per scheduled run; the next run takes the rest.
EXPIRY_BATCH = 100

# Shown to learners before they practice, by language; the pass mark comes from
# CERTIFICATE_MIN_SCORE.
CERTIFICATE_RULES = {
    "en": [
        "Answer every question of the topic.",
        "Only your latest answer to each question counts.",
        f"At least {CERTIFICATE_MIN_SCORE}% of your answers must be correct.",
        "Once all of the above are done, you'll receive your certificate.",
    ],
    "ru": [
        "Ответьте на все вопросы темы.",
        "Учитывается только последний ответ на каждый вопрос.",
        f"Не меньше {CERTIFICATE_MIN_SCORE}% ответов должны быть верными.",
        "Когда всё это выполнено, вы получите сертификат.",
    ],
}
