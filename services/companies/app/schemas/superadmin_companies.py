from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.constants.verification import VerificationStatus
from app.schemas.companies import CompanyName


class SuperadminCompanyOut(BaseModel):
    id: UUID
    name: str
    verification_status: VerificationStatus
    verified_domain: str | None
    members: int
    suspended: bool
    created_at: datetime


class CompanyNameIn(BaseModel):
    name: CompanyName
