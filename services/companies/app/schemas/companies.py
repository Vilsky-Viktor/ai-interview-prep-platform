from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class MemberOut(BaseModel):
    email: str
    role: str
    joined: bool
    token: str | None = None
    created_at: datetime


class AdminInviteOut(BaseModel):
    """What the invited admin sees before accepting."""

    company_name: str
    email: str
    joined: bool


class CompanyOut(BaseModel):
    id: UUID
    name: str
    role: str
    interview_count: int
    created_at: datetime


class MemberIn(BaseModel):
    email: EmailStr


class CompanyCreditsOut(BaseModel):
    available: int
    low: bool


class CompanyBalanceOut(BaseModel):
    """A company the user can top up, with its credits."""

    id: UUID
    name: str
    available: int
    low: bool
