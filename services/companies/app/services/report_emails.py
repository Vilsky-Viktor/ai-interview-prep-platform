from fastapi import HTTPException, status
from prepza_common.rate_limit import hit, hit_emails
from prepza_common.user import User

from app.constants.reports import NO_FINISHED_CANDIDATES, NOT_A_PDF, TOO_MANY_REPORT_EMAILS
from app.helpers.reports import is_report_pdf
from app.integrations.redis import get_redis
from app.models.companies import Company
from app.models.interviews import Interview
from app.storage import candidates


async def allow_report_email(
    user: User, company: Company, interview: Interview, pdf: str, recipient: str
) -> None:
    """Refuses a report email unless a candidate finished the interview and the PDF is one; then
    counts it towards the member's email limits and the company's daily reports."""
    if not await candidates.any_finished(interview.id):
        raise HTTPException(status.HTTP_409_CONFLICT, NO_FINISHED_CANDIDATES)

    if not is_report_pdf(pdf):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, NOT_A_PDF)

    redis = get_redis()
    await hit_emails(redis, user.uid, recipient, company.id)
    await hit(
        redis,
        f"rate:report-emails:day:{company.id}",
        "REPORT_EMAILS_PER_COMPANY_DAY",
        TOO_MANY_REPORT_EMAILS,
        company_id=company.id,
        user_id=user.uid,
    )
