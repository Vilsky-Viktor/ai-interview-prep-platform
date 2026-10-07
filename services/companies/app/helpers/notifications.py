from prepza_common.notifications import NotificationKind, Recipient, notification

from app.constants.notifications import ATS_LINK, INTERVIEW_LINK, INTERVIEWS_LINK
from app.constants.roles import EDITORS
from app.models.companies import Company
from app.models.interviews import Interview


def interview_link(interview: Interview) -> str:
    return INTERVIEW_LINK.format(company_id=interview.company_id, interview_id=interview.id)


def candidate_finished(interview: Interview, invite_id: str, email: str, grade: int | None) -> dict:
    """The grade is left out while rounds has none. One per invite, though a retried event
    finishes the candidate again."""
    data = {"email": email, "title": interview.title}

    if grade is not None:
        data["grade"] = grade

    return notification(
        Recipient.COMPANY,
        interview.company_id,
        NotificationKind.CANDIDATE_FINISHED,
        interview_link(interview),
        key=str(invite_id),
        **data,
    )


def invite_undelivered(interview: Interview, email: str) -> dict:
    return notification(
        Recipient.COMPANY,
        interview.company_id,
        NotificationKind.INVITE_UNDELIVERED,
        interview_link(interview),
        email=email,
        title=interview.title,
    )


def interview_ready(interview: Interview, title: str) -> dict:
    """One per interview, though a retried event saves its questions again."""
    return notification(
        Recipient.COMPANY,
        interview.company_id,
        NotificationKind.INTERVIEW_READY,
        interview_link(interview),
        key=str(interview.id),
        title=title,
    )


def interview_cancelled(interview: Interview) -> dict:
    """A cancelled interview never got its questions, so it rarely has a title."""
    data = {"title": interview.title} if interview.title else {}

    return notification(
        Recipient.COMPANY,
        interview.company_id,
        NotificationKind.INTERVIEW_CANCELLED,
        INTERVIEWS_LINK.format(company_id=interview.company_id),
        **data,
    )


def verification_decided(company: Company, approved: bool, reason: str | None) -> list[dict]:
    """One for each of the company's owners and admins (viewers can't act on it); a decline
    says why when the superadmin did."""
    kind = (
        NotificationKind.VERIFICATION_APPROVED
        if approved
        else NotificationKind.VERIFICATION_DECLINED
    )
    data = {"name": company.verification_name or company.name, "domain": company.website_domain}

    if reason:
        data["reason"] = reason

    return [
        notification(
            Recipient.USER,
            member.user_id,
            kind,
            INTERVIEWS_LINK.format(company_id=company.id),
            **data,
        )
        for member in company.members
        if member.user_id and member.role in EDITORS
    ]


def ats_not_invited(interview: Interview, email: str, reason: str) -> dict:
    """A candidate the ATS sent who wasn't invited, and why; the ATS tab retries. Several at
    once add up to one notification."""
    return notification(
        Recipient.COMPANY,
        interview.company_id,
        NotificationKind.ATS_NOT_INVITED,
        ATS_LINK.format(company_id=interview.company_id),
        email=email,
        title=interview.title,
        reason=reason,
    )
