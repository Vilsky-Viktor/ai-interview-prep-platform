from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.constants.rounds import Mode, RoundStatus
from app.schemas.library import TopicQuestions
from app.schemas.review import ReviewItem


class InviteScoresIn(BaseModel):
    invite_ids: list[UUID]


class SessionsCreate(BaseModel):
    user_id: str
    candidate_invite_id: UUID
    mode: Mode
    share_results: bool
    topics: list[TopicQuestions]


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
    mode: Mode
    share_results: bool
    status: RoundStatus
    total: int
    answered: int
    current_score: int | None
    final_score: int | None
    started_at: datetime
    finished_at: datetime | None


class SessionAnswerResult(BaseModel):
    answer_id: UUID
    answered: int
    total: int
    correct: bool | None = None
    score: int | None = None
    feedback: str | None = None
    current_score: int | None = None


class ScorecardSession(BaseModel):
    id: UUID
    topic_title: str
    mode: Mode
    status: RoundStatus
    final_score: int | None
    review: list[ReviewItem]
