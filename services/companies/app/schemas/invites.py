from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class CandidateIn(BaseModel):
    email: EmailStr


class CandidateOut(BaseModel):
    id: UUID
    email: str
    status: str
    progress: int = 0
    grade: int | None = None
    created_at: datetime


class InviteView(BaseModel):
    interview_id: UUID
    title: str | None
    company: str
    email: str
    status: str
    # Shown before the candidate starts: the timer begins at start.
    time_limit_minutes: int | None


class SessionSummary(BaseModel):
    id: UUID
    topic_title: str
    status: str
    final_score: int | None = None


class InviteStartOut(BaseModel):
    sessions: list[SessionSummary]
