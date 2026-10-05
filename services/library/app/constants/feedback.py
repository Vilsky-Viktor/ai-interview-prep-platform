from enum import StrEnum


class ReportReason(StrEnum):
    WRONG_ANSWER = "wrong_answer"
    UNCLEAR = "unclear"
    OFF_TOPIC = "off_topic"
    OTHER = "other"


class ReportStatus(StrEnum):
    OPEN = "open"


MAX_REPORT_COMMENT_LENGTH = 1000
