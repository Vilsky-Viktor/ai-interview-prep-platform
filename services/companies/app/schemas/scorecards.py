"""A candidate's scorecard: their invite and overall result from companies, and each section
with its questions and answers from rounds."""

from uuid import UUID

from pydantic import BaseModel


class ScorecardAnswer(BaseModel):
    answer_id: UUID
    # None when a timed question ran out first.
    option_index: int | None
    correct: bool | None
    seconds: int | None = None
    # Answered faster than rounds' FAST_ANSWER_SECONDS.
    fast: bool = False


class ScorecardQuestion(BaseModel):
    question_id: UUID
    number: int
    text: str
    options: list[str]
    # Only once the question is answered.
    correct_option_index: int | None
    answer: ScorecardAnswer | None
    # Page leaves and copy attempts while this question was open.
    tab_leaves: int = 0
    copies: int = 0


class ScorecardSection(BaseModel):
    """One topic's round."""

    id: UUID
    topic_title: str
    status: str
    final_score: int | None
    tab_leaves: int
    copies: int
    fast_answers: int
    review: list[ScorecardQuestion]
    # None while the section is still going.
    passed: bool | None


class ScorecardOut(BaseModel):
    id: UUID
    email: str
    # The name from the candidate's sign-in; None until they start, or when it has none.
    name: str | None = None
    status: str
    extra_time: int
    # Whether the user may change the candidate (extra time, revoke): not a viewer.
    can_edit: bool
    # What extra time can still be given: only before the candidate starts, and not by a viewer.
    extra_time_options: list[int]
    # The invite link's token, to copy and send in case the email didn't arrive or got lost: until
    # the candidate finishes, while the link works (not expired), and not for a viewer.
    invite_token: str | None = None
    # For the PDF report: the test, the company, and the overall result.
    title: str | None
    company: str
    logo_url: str | None
    verified_domain: str | None
    grade: int | None
    # None until the candidate finishes.
    passed: bool | None
    pass_mark: int
    sessions: list[ScorecardSection]
