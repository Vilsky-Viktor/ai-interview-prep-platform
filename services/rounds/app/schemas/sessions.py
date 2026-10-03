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
    topics: list[TopicQuestions]
    # Every interview is timed: the seconds each question has.
    question_seconds: int = Field(ge=1)


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
    status: RoundStatus
    total: int
    answered: int
    started_at: datetime
    finished_at: datetime | None
    # The seconds each question has; None for sessions from before every interview was timed.
    question_seconds: int | None


class SessionAnswerResult(BaseModel):
    answer_id: UUID
    answered: int
    total: int


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
