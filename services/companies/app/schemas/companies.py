from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.constants.invites import MAX_COMPANY_NAME_LENGTH
from app.constants.roles import Role


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=MAX_COMPANY_NAME_LENGTH)


class CompanyRename(BaseModel):
    """A new name, edited in place like a test's title (hence `title`)."""

    title: str = Field(min_length=1, max_length=MAX_COMPANY_NAME_LENGTH)


class MemberOut(BaseModel):
    id: UUID
    email: str
    role: str
    joined: bool
    token: str | None = None
    # Whether the user can remove this member or pending invite, or change its role: the owner,
    # any row but their own.
    removable: bool = False
    created_at: datetime


class AdminInviteOut(BaseModel):
    """What the invited member sees before accepting."""

    company_name: str
    email: str
    joined: bool


class CompanyOut(BaseModel):
    id: UUID
    name: str
    role: str
    # Owners and admins change things and spend credits; viewers only look and share reports.
    can_edit: bool
    interview_count: int
    # The logo's address on the site; None until one is set.
    logo_url: str | None = None
    # The website's domain, and the same once verified by an admin's work email (the badge).
    website_domain: str | None = None
    verified_domain: str | None = None
    created_at: datetime


# The roles the owner gives a member.
MemberRole = Literal[Role.ADMIN, Role.VIEWER]


class MemberIn(BaseModel):
    email: EmailStr
    role: MemberRole = Role.ADMIN


class MemberRoleIn(BaseModel):
    role: MemberRole


class ReferralRewardOut(BaseModel):
    """A company that came through the link and topped up; no name once it's deleted."""

    name: str | None
    rewarded_at: datetime


class ReferralOut(BaseModel):
    """The company's referral link code, what it earns, how many it has earned for, and the latest
    of those, newest first."""

    code: str
    reward: int
    rewarded: int
    rewards: list[ReferralRewardOut]


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
