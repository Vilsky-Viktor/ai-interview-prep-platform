from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser

from app.constants.audit import AuditAction
from app.constants.invites import InviteStatus
from app.helpers.candidates import candidate_label, candidate_out
from app.helpers.interviews import interview_title
from app.helpers.logos import logo_path
from app.integrations import rounds
from app.schemas.reports import InterviewReportOut, ReportEmailIn
from app.services import candidate_results
from app.services import outbox as outbox_service
from app.services.access import require_company
from app.services.report_emails import allow_report_email
from app.storage import audit, candidates, interviews, reports

router = APIRouter(prefix="/interviews", tags=["reports"])


@router.post(
    "/{interview_id}/candidates/{invite_id}/report/email", status_code=status.HTTP_202_ACCEPTED
)
async def email_report(
    interview_id: UUID, invite_id: UUID, body: ReportEmailIn, user: CurrentUser
) -> None:
    """Emails the candidate's PDF report, made on their page, to someone such as a hiring
    manager. A reply goes to the member who sent it. Counts towards the member's email limits
    and the company's daily reports."""
    interview = await interviews.get(interview_id)
    invite = await candidates.get(interview_id, invite_id) if interview else None

    if interview is None or invite is None or invite.status == InviteStatus.DELETED:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate not found")

    company, _ = await require_company(user, interview.company_id)

    email = str(body.email).lower()
    await allow_report_email(user, company, interview, body.pdf, f"report:{invite.id}:{email}")
    await reports.queue_email(
        {
            "email": email,
            "sender": user.name or user.email,
            "reply_to": user.email,
            "company": company.name,
            "title": await interview_title(interview) or "",
            "candidate": candidate_label(invite),
            "language": interview.language,
            "filename": f"Report {invite.email}.pdf",
            "pdf": body.pdf,
        }
    )
    await audit.record(company.id, user.uid, AuditAction.REPORT_EMAILED, invite.id)
    await outbox_service.flush_quietly()


@router.get("/{interview_id}/report")
async def interview_report(interview_id: UUID, user: CurrentUser) -> InterviewReportOut:
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    company, _ = await require_company(user, interview.company_id)
    await candidate_results.backfill(interview.id)
    every = await candidates.for_report(interview.id)
    totals = await rounds.invite_scores([invite.id for invite in every])

    return InterviewReportOut(
        title=await interview_title(interview),
        company=company.name,
        logo_url=logo_path(company),
        verified_domain=company.verified_domain,
        pass_mark=interview.pass_mark,
        candidates=[
            candidate_out(invite, totals.get(str(invite.id)) or {}, interview) for invite in every
        ],
    )


@router.post("/{interview_id}/report/email", status_code=status.HTTP_202_ACCEPTED)
async def email_interview_report(
    interview_id: UUID, body: ReportEmailIn, user: CurrentUser
) -> None:
    """Emails the test's candidates report, made on its candidates tab, like a candidate's."""
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    company, _ = await require_company(user, interview.company_id)

    email = str(body.email).lower()
    await allow_report_email(user, company, interview, body.pdf, f"report:{interview.id}:{email}")
    title = await interview_title(interview) or ""
    await reports.queue_email(
        {
            "kind": "candidates",
            "email": email,
            "sender": user.name or user.email,
            "reply_to": user.email,
            "company": company.name,
            "title": title,
            "language": interview.language,
            "filename": f"Candidates {title}.pdf".strip(),
            "pdf": body.pdf,
        }
    )
    await audit.record(company.id, user.uid, AuditAction.REPORT_EMAILED, interview.id)
    await outbox_service.flush_quietly()
