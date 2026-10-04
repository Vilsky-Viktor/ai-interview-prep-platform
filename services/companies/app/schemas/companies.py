from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.constants.invites import MAX_COMPANY_NAME_LENGTH


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=MAX_COMPANY_NAME_LENGTH)


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


class ReferralOut(BaseModel):
    """The company's referral link code, what it earns, and how many it has earned for."""

    code: str
    reward: int
    min_dollars: int
    rewarded: int


class CompanyCreditsOut(BaseModel):
    available: int
    low: bool


class CompanyBalanceOut(BaseModel):
    """A company the user can top up, with its credits."""

    id: UUID
    name: str
    available: int
    low: bool


class UserCompaniesOut(BaseModel):
    """Every company the user is a member of, for the notifications service."""

    company_ids: list[str]
