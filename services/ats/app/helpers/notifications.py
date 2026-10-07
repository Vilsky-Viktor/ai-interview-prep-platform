from prepza_common.notifications import NotificationKind, Recipient, notification

from app.constants.notifications import ATS_LINK


def ats_not_invited(company_id, ats: str, title: str | None, email: str, reason: str) -> dict:
    """A candidate the ATS named `ats` sent who wasn't invited, and why; the ATS tab retries.
    Several at once add up to one notification."""
    return notification(
        Recipient.COMPANY,
        company_id,
        NotificationKind.ATS_NOT_INVITED,
        ATS_LINK.format(company_id=company_id),
        ats=ats,
        email=email,
        title=title,
        reason=reason,
    )
