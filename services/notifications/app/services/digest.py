from datetime import datetime, timedelta

from app.config.settings import settings
from app.constants.member_emails import DIGEST_HOURS, MemberEmail
from app.constants.unsubscribe import DIGEST_KINDS
from app.helpers.member_emails import digest_email
from app.helpers.member_selection import digest_sections
from app.integrations import companies, library
from app.services.member_sends import deadline, send_once
from app.storage import notifications


async def send_digests(now: datetime) -> int:
    """The activity digest: one email a day to each member of a company that had activity of a
    kind they get, in the 24 hours before the hour this run is in (the same for every run that
    hour), covering all their companies. Returns how many were sent."""
    until = now.replace(minute=0, second=0, microsecond=0)
    stop = deadline()
    activity = await notifications.companies_activity(
        DIGEST_KINDS, until - timedelta(hours=DIGEST_HOURS), until
    )

    if not activity:
        return 0

    found = await companies.members(sorted({item.recipient_id for item in activity}))
    user_ids = sorted({member["user_id"] for company in found for member in company["members"]})
    site = settings.site_url.rstrip("/")
    jobs = []

    for recipient in await library.recipients(user_ids):
        sections = digest_sections(
            recipient["user_id"], recipient["preferences"], found, activity, site
        )

        if sections:
            jobs.append((recipient["user_id"], [], email_for(recipient, sections)))

    return await send_once(MemberEmail.DIGEST, until.date(), 1, jobs, stop)


def email_for(recipient: dict, sections: list):
    return lambda new: digest_email(
        recipient, sections, settings.site_url, settings.email_link_secret
    )
