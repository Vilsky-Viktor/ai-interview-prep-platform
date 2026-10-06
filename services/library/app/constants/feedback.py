from enum import StrEnum


class ReportReason(StrEnum):
    WRONG_ANSWER = "wrong_answer"
    UNCLEAR = "unclear"
    OFF_TOPIC = "off_topic"
    OTHER = "other"


class ReportStatus(StrEnum):
    OPEN = "open"


MAX_REPORT_COMMENT_LENGTH = 1000
# Reports and thumbs a user may send a day: reports and dislikes flag questions for a rewrite,
# which costs model calls.
REPORTS_PER_DAY = 30
RATINGS_PER_DAY = 200
