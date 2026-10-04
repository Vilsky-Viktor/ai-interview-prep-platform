from prepza_common.notifications import NotificationKind, Recipient, notification

from app.constants.notifications import INTERVIEW_LINK, INTERVIEWS_LINK
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
