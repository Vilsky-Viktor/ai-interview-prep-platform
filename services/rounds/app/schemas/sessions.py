from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.constants.rounds import RoundStatus
from app.schemas.library import TopicQuestions
from app.schemas.review import ReviewItem


class InviteScoresIn(BaseModel):
    invite_ids: list[UUID]


class SessionsCreate(BaseModel):
    user_id: str
    candidate_invite_id: UUID
    share_results: bool
    topics: list[TopicQuestions]
    # Set for a timed interview: the candidate has this long from now for every section.
    time_limit_minutes: int | None = Field(default=None, ge=1)


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
    # Timed interviews only: when the interview finishes by itself.
    deadline: datetime | None


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
    review: list[ReviewItem]


class MasteredCountsIn(BaseModel):
    user_id: str
    preparation_ids: list[UUID]
