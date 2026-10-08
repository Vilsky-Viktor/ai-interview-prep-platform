import logging
from uuid import UUID

from app.constants.events import COMPANY_DELETED
from app.storage import conversations

logger = logging.getLogger(__name__)


async def handle(event_type: str, data: dict) -> None:
    """company.deleted: the company's conversations go. Safe on a redelivery: nothing is left
    to delete. Other events are ignored."""
    if event_type != COMPANY_DELETED:
        return

    try:
        company_id = UUID(str(data.get("company_id")))
    except ValueError:
        # Retrying can't fix it: dropped, so Pub/Sub doesn't send it again and again.
        logger.warning("Dropped company.deleted for a malformed company %r", data.get("company_id"))

        return

    deleted = await conversations.delete_company(company_id)

    if deleted:
        logger.info("Deleted %d assistant conversations of a deleted company", deleted)
