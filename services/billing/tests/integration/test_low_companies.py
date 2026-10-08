import uuid

from app.constants.credits import CANDIDATE_CREDITS
from app.constants.products import OwnerType
from app.models.billing import Wallet
from app.storage import auto_top_ups as rows
from app.storage import ledger
from app.storage.db import Session

COMPANY = OwnerType.COMPANY


async def wallet(available: int) -> str:
    owner = str(uuid.uuid4())

    async with Session() as session:
        session.add(Wallet(owner_type=COMPANY, owner_id=owner, balance=available, reserved=0))
        await session.commit()

    return owner


def test_running_low_lists_companies_short_of_a_candidate_unless_a_top_up_refills_them(run):
    async def scenario():
        low = await wallet(CANDIDATE_CREDITS - 1)
        enough = await wallet(CANDIDATE_CREDITS)
        refilled = await wallet(0)
        await rows.save(COMPANY, refilled, "topup_30", 300, "ann")
        await rows.start(COMPANY, refilled, "ann", f"sub_{uuid.uuid4().hex[:12]}")
        found = {row.owner_id for row in await ledger.running_low(COMPANY)}

        return found & {low, enough, refilled}, low

    found, low = run(scenario())

    assert found == {low}
