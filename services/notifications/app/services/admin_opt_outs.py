import logging

from fastapi import HTTPException, status

from app.helpers.unsubscribe import address_hash
from app.integrations import companies
from app.storage import opt_outs

logger = logging.getLogger(__name__)


async def companies_for(email: str) -> list[dict]:
    """The companies that invited the address or whose emails it stopped, by name, with what it
    stopped; a company that's gone is left out."""
    rows = await opt_outs.of_address(address_hash(email))
    ids = set(await companies.invited_company_ids(email)) | {row.company_id for row in rows}
    found = await companies.members(sorted(ids))

    return sorted(
        (
            {
                "company_id": company["id"],
                "name": company["name"],
                "stopped": any(
                    row.company_id == company["id"] and row.invite_id is None for row in rows
                ),
                "stopped_reminders": sum(
                    row.company_id == company["id"] and row.invite_id is not None for row in rows
                ),
            }
            for company in found
        ),
        key=lambda company: company["name"].lower(),
    )


async def set_stopped(email: str, company_id: str, stopped: bool, superadmin_id: str) -> None:
    """Stops every email from a company that invited the address, or lets them all through
    again (reminders too). Safe to repeat. Who did it goes to the logs, without the address."""
    address = address_hash(email)

    if stopped:
        if company_id not in await companies.invited_company_ids(email):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")

        await opt_outs.add(address, company_id)
    else:
        await opt_outs.remove(address, company_id)

    logger.warning(
        "Company %s's emails to address %s %s by superadmin %s",
        company_id,
        address,
        "stopped" if stopped else "let through again",
        superadmin_id,
    )
