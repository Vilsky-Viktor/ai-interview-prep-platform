from datetime import datetime, timedelta

from app.config.settings import settings
from app.constants.member_emails import (
    NO_CANDIDATES_DAYS,
    NO_CANDIDATES_WINDOW_DAYS,
    REMINDER_DAYS,
    REVIEW_STARTED_DAYS,
    REVIEW_WAITING_DAYS,
    MemberEmail,
)
from app.helpers.member_emails import reminder_email
from app.helpers.member_selection import awaiting_review, editors, interview_rows, low_credit_rows
from app.integrations import billing, companies, generation, library
from app.services.member_sends import deadline, send_once


async def send_reminders(now: datetime) -> int:
    """Reminders to owners and admins who get them: companies running low on credits,
    interviews nobody was invited to NO_CANDIDATES_DAYS after they were ready, and, to whoever
    started one, topics waiting for a review for REVIEW_WAITING_DAYS. Each kind at most once in
    REMINDER_DAYS to a user, and each interview named once. Returns how many were sent."""
    stop = deadline()
    low = await billing.low_companies()
    waiting = await companies.waiting_interviews(
        (now - timedelta(days=NO_CANDIDATES_WINDOW_DAYS), now - timedelta(days=NO_CANDIDATES_DAYS)),
        (now - timedelta(days=REVIEW_STARTED_DAYS), now - timedelta(days=REVIEW_WAITING_DAYS)),
    )
    idle, generating = waiting["without_candidates"], waiting["being_generated"]
    statuses = await generation.statuses([found["generation_id"] for found in generating])
    company_ids = {found["company_id"] for found in low} | {
        found["company_id"] for found in idle + generating
    }
    found = await companies.members(sorted(company_ids))
    site = settings.site_url.rstrip("/")
    can_act = editors(found)
    reviews, starters = awaiting_review(generating, statuses, now, found)
    rows = {
        MemberEmail.LOW_CREDITS: low_credit_rows(low, found, site),
        MemberEmail.NO_CANDIDATES: interview_rows(
            idle,
            {interview["id"]: can_act.get(interview["company_id"], []) for interview in idle},
            found,
            site,
            lambda interview, company: {"title": interview["title"] or "", "company": company},
        ),
        MemberEmail.REVIEW_WAITING: interview_rows(
            reviews,
            starters,
            found,
            site,
            lambda interview, company: {"days": interview["days"], "company": company},
        ),
    }
    user_ids = sorted({user_id for by_user in rows.values() for user_id in by_user})
    recipients = [
        recipient
        for recipient in await library.recipients(user_ids)
        if recipient["preferences"]["reminders"]
    ]
    sent = 0

    for kind, by_user in rows.items():
        jobs = [
            (
                recipient["user_id"],
                tracked(kind, by_user[recipient["user_id"]]),
                email_for(kind, recipient, by_user[recipient["user_id"]]),
            )
            for recipient in recipients
            if recipient["user_id"] in by_user
        ]
        sent += await send_once(kind, now.date(), REMINDER_DAYS, jobs, stop)

    return sent


def tracked(kind: MemberEmail, items: list) -> list[str]:
    """What a reminder names that it mustn't name again: interviews. Credits are reminded
    about again each REMINDER_DAYS while they stay low."""
    if kind == MemberEmail.LOW_CREDITS:
        return []

    return [item_id for item_id, _ in items]


def email_for(kind: MemberEmail, recipient: dict, items: list):
    """Builds the reminder from the items not named before (all of them for credits)."""

    def build(new: list[str]):
        rows = [row for item_id, row in items if not new or item_id in new]

        return reminder_email(kind, recipient, rows, settings.site_url, settings.email_link_secret)

    return build
