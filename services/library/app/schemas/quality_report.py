from datetime import datetime
from uuid import UUID

from prepza_common.sets import OptionIn
from pydantic import BaseModel


class FlaggedQuestionOut(BaseModel):
    """A question flagged now, for the admin zone's quality tab."""

    question_id: UUID
    text: str
    options: list[OptionIn]
    flag: str
    # A template's questions can be fixed now or dismissed here; a company's only viewed.
    actionable: bool
    answers: int
    correct: int
    reports: int
    set_title: str
    # A template, or a company's test.
    set_kind: str
    # When it was flagged.
    at: datetime


class ReplacedQuestionOut(BaseModel):
    """A question's old content, kept when it was replaced."""

    # The kept revision, whose reports can be listed.
    revision_id: UUID
    question_id: UUID
    # Its old text and options, as they were before it was replaced.
    text: str
    options: list[OptionIn]
    answers: int
    correct: int
    reports: int
    set_title: str
    set_kind: str
    # When it was replaced.
    at: datetime
