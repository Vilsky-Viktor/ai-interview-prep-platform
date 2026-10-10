from prepza_common.notifications import NotificationKind, Recipient, notification

from app.constants.notifications import ATS_LINK


def ats_not_invited(
    company_id,
    provider: str,
    ats: str,
    title: str | None,
    email: str,
    reason: str,
    name: str | None = None,
) -> dict:
    """A candidate the ATS named `ats` sent who wasn't invited (with their name, if it sent
    one), and why; that ATS's page, which the notification opens, retries. Several at once add up to one notification."""
    return notification(
        Recipient.COMPANY,
        company_id,
        NotificationKind.ATS_NOT_INVITED,
        ATS_LINK.format(company_id=company_id, provider=provider),
        ats=ats,
        email=email,
        title=title,
        reason=reason,
        **({"candidate_name": name} if name else {}),
    )
