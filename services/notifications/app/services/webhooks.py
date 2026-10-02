from app.constants.webhooks import (
    CANDIDATE_INVITE_KIND,
    ID_TAG,
    KIND_TAG,
    SHARE_KIND,
    UNDELIVERED_EVENTS,
)
from app.integrations import companies, library


async def handle(event: dict) -> None:
    """Tells the invite's owner its email wasn't delivered; other events and untagged emails
    aren't ours to report."""
    if event.get("type") not in UNDELIVERED_EVENTS:
        return

    tags = (event.get("data") or {}).get("tags") or {}
    kind, invite_id = tags.get(KIND_TAG), tags.get(ID_TAG)

    if not invite_id:
        return

    if kind == CANDIDATE_INVITE_KIND:
        await companies.invite_undelivered(invite_id)

    if kind == SHARE_KIND:
        await library.share_undelivered(invite_id)
