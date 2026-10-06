from fastapi import HTTPException, status
from prepza_common.constants import DAY_SECONDS
from prepza_common.rate_limit import hit, hit_emails
from prepza_common.user import User

from app.config.settings import settings
from app.constants.invites import InviteStatus
from app.constants.reports import NO_FINISHED_CANDIDATES, NOT_A_PDF, TOO_MANY_REPORT_EMAILS
from app.helpers.reports import is_report_pdf
from app.integrations.redis import get_redis
from app.models.companies import Company
from app.models.interviews import Interview


async def allow_report_email(
    user: User, company: Company, interview: Interview, pdf: str, recipient: str
) -> None:
    """Refuses a report email unless a candidate finished the interview and the PDF is one; then
    counts it towards the member's email limits and the company's daily reports."""
    if not any(invite.status == InviteStatus.FINISHED for invite in interview.invites):
        raise HTTPException(status.HTTP_409_CONFLICT, NO_FINISHED_CANDIDATES)

    if not is_report_pdf(pdf):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, NOT_A_PDF)

    redis = get_redis()
    await hit_emails(
        redis,
        user.uid,
        recipient,
        settings.email_hourly_limit,
        settings.email_daily_limit,
        settings.email_recipient_daily_limit,
    )
    await hit(
        redis,
        f"rate:report-emails:day:{company.id}",
        settings.report_emails_per_company_day,
        DAY_SECONDS,
        TOO_MANY_REPORT_EMAILS,
    )
