from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.constants.integrity import IntegritySignal
from app.constants.rounds import RoundStatus
from app.schemas.library import TopicQuestions
from app.schemas.review import ReviewItem


class InviteScoresIn(BaseModel):
    invite_ids: list[UUID]


class InviteIdsIn(BaseModel):
    invite_ids: list[UUID]


class SessionsCreate(BaseModel):
    user_id: str
    candidate_invite_id: UUID
    share_results: bool
    topics: list[TopicQuestions]
    # Set for a timed interview: the seconds each question has.
    question_seconds: int | None = Field(default=None, ge=1)


class SessionTopicOut(BaseModel):
    id: UUID
    topic_title: str
    status: RoundStatus
    total: int
    answered: int


class SessionOut(BaseModel):
    id: UUID
    topic_id: UUID
    topic_title: str
    interview_title: str | None = None
    share_results: bool
    status: RoundStatus
    total: int
    answered: int
    current_score: int | None
    final_score: int | None
    # Whether the score shown passes; None when there is none or results aren't shared.
    passed: bool | None
    started_at: datetime
    finished_at: datetime | None
    # Timed interviews only: the seconds each question has.
    question_seconds: int | None


class SessionAnswerResult(BaseModel):
    answer_id: UUID
    answered: int
    total: int
    # Only when the candidate may see results.
    correct: bool | None = None
    current_score: int | None = None
    passed: bool | None = None


class ScorecardSession(BaseModel):
    id: UUID
    topic_title: str
    status: RoundStatus
    final_score: int | None
    # Integrity signals: times the candidate left the tab, copy attempts, and answers faster
    # than FAST_ANSWER_SECONDS.
    tab_leaves: int
    copies: int
    fast_answers: int
    review: list[ReviewItem]


class SignalIn(BaseModel):
    kind: IntegritySignal


class MasteredCountsIn(BaseModel):
    user_id: str
    preparation_ids: list[UUID]
