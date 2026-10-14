import time
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from prepza_common.constants import LEGAL_VERSIONS

from app.config.settings import settings
from app.constants.legal_notices import (
    ALREADY_ASKED,
    EVERYONE,
    LEGAL_NOTICE_DAYS,
    TOO_LATE,
    LegalNoticeState,
)
from app.helpers.member_emails import legal_email
from app.integrations import companies, library
from app.services.member_sends import deadline, send_once
from app.storage import legal_notices


def earliest_version(today) -> str:
    """The earliest day a version can apply from to be noticed today."""
    return (today + timedelta(days=LEGAL_NOTICE_DAYS)).isoformat()


async def states() -> list[dict]:
    """Each document's current version, and where its notice stands."""
    asked = {(row.document, row.version): row for row in await legal_notices.all_notices()}
    today = datetime.now(UTC).date()
    earliest = earliest_version(today)
    found = []

    for document, version in LEGAL_VERSIONS.items():
        row = asked.get((document, version))

        if row is not None:
            state = LegalNoticeState.SENT if row.sent_at else LegalNoticeState.SENDING
        elif version <= today.isoformat():
            state = LegalNoticeState.IN_FORCE
        elif version < earliest:
            state = LegalNoticeState.TOO_LATE
        else:
            state = LegalNoticeState.SENDABLE

        audience = "everyone" if document in EVERYONE else "company_editors"
        found.append(
            {"document": document, "version": version, "state": state, "audience": audience}
        )

    return found


async def ask(document: str, user_id: str) -> None:
    """A superadmin asks for the email about the document's current version: refused when it
    applies sooner than LEGAL_NOTICE_DAYS from now, or was asked for already."""
    version = LEGAL_VERSIONS[document]

    if version < earliest_version(datetime.now(UTC).date()):
        raise HTTPException(status.HTTP_409_CONFLICT, TOO_LATE)

    if not await legal_notices.ask(document, version, user_id):
        raise HTTPException(status.HTTP_409_CONFLICT, ALREADY_ASKED)


async def send_legal_notices(now: datetime) -> int:
    """Each notice asked for and not yet sent to everyone: to every account (the terms, the
    privacy policy) or every company's owner and admin (the DPA), once each. A run that ends
    before its time is up has sent them all."""
    stop = deadline()
    sent = 0

    for notice in await legal_notices.all_notices():
        if notice.sent_at is not None:
            continue

        ids = await (library.user_ids() if notice.document in EVERYONE else companies.editor_ids())
        jobs = [
            (
                recipient["user_id"],
                [notice.version],
                email_for(recipient, notice.document, notice.version),
            )
            for recipient in await library.recipients(ids)
        ]
        sent += await send_once(f"legal_{notice.document}", now.date(), 1, jobs, stop)

        if time.monotonic() > stop:
            break

        await legal_notices.sent(notice.document, notice.version)

    return sent


def email_for(recipient: dict, document: str, version: str):
    return lambda new: legal_email(recipient, document, version, settings.site_url)
