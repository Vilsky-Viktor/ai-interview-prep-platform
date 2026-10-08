from uuid import UUID

from app.constants.events import CANDIDATE_FINISHED, CANDIDATE_RESCORED, COMPANY_DELETED
from app.services import webhooks as webhook_events
from app.storage import keys, webhooks


async def handle(event_type: str, data: dict, event_id: str) -> None:
    """Companies' events. Each is safe to run again on a redelivery: a web hook gets an event
    once (its deliveries), and deleting twice deletes nothing more. Other events are ignored."""
    if event_type in (CANDIDATE_FINISHED, CANDIDATE_RESCORED):
        await webhook_events.notify(event_type, data, event_id)
    elif event_type == COMPANY_DELETED:
        company_id = UUID(data["company_id"])
        await keys.remove_company(company_id)
        await webhooks.remove_company(company_id)
