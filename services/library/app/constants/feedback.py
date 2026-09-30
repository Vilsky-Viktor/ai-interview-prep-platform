from enum import StrEnum


class ReportReason(StrEnum):
    WRONG_ANSWER = "wrong_answer"
    UNCLEAR = "unclear"
    OFF_TOPIC = "off_topic"
    OTHER = "other"


class ReportStatus(StrEnum):
    OPEN = "open"


MIN_RATING = 1
MAX_RATING = 5
MAX_REPORT_COMMENT_LENGTH = 1000

# Library ranking starts every preparation with this many imaginary ratings of this value, so a
# single 5-star vote doesn't outrank dozens of good ratings.
RATING_PRIOR_MEAN = 3.0
RATING_PRIOR_WEIGHT = 5
