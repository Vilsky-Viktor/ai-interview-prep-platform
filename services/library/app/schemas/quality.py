from prepza_common.sets import OptionIn
from pydantic import BaseModel


class ReportNote(BaseModel):
    reason: str
    comment: str


class QuestionQuality(BaseModel):
    """What the verifier looks at: the question, how it's answered and what users reported."""

    text: str
    options: list[OptionIn]
    answers: int
    option_picks: dict[str, int]
    reports: list[ReportNote]
