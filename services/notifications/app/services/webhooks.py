from app.constants.webhooks import CANDIDATE_INVITE_KIND, ID_TAG, KIND_TAG, UNDELIVERED_EVENTS
from app.integrations import companies


async def handle(event: dict) -> None:
    """Tells the invite's owner its email wasn't delivered; other events and untagged emails
    aren't ours to report."""
    if event.get("type") not in UNDELIVERED_EVENTS:
        return

    await report_undelivered((event.get("data") or {}).get("tags") or {})


async def report_undelivered(tags: dict[str, str]) -> None:
    """Marks the invite the email was for as undelivered, from its tags."""
    kind, invite_id = tags.get(KIND_TAG), tags.get(ID_TAG)

    if not invite_id:
        return

    if kind == CANDIDATE_INVITE_KIND:
        await companies.invite_undelivered(invite_id)
