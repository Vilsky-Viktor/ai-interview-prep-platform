from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.constants.invites import MAX_COMPANY_NAME_LENGTH
from app.constants.verification import VerificationStatus


class SuperadminCompanyOut(BaseModel):
    id: UUID
    name: str
    verification_status: VerificationStatus
    verified_domain: str | None
    members: int
    suspended: bool
    created_at: datetime


class CompanyNameIn(BaseModel):
    name: str = Field(min_length=1, max_length=MAX_COMPANY_NAME_LENGTH)
