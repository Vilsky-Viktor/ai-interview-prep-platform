import uuid
from datetime import UTC, datetime

from app.constants.credits import WELCOME_COMPANY, Reason
from app.constants.products import AUTO_TOP_UP_COOLDOWN, OwnerType
from app.schemas.billing import AutoTopUpIn
from app.services import auto_top_ups
from app.services.topups import handle_completed
from app.storage import auto_top_ups as rows
from app.storage import ledger
from tests.integration.test_auto_top_ups import checkout_data

COMPANY = OwnerType.COMPANY


def test_once_a_charges_credits_come_the_next_charge_waits_only_the_cooldown(run, paddle_calls):
    ann = f"user-{uuid.uuid4()}"
    acme = str(uuid.uuid4())
    sub = f"sub_{uuid.uuid4().hex[:12]}"

    async def scenario():
        await ledger.welcome_company(acme, f"{acme}@example.com")
        await auto_top_ups.turn_on(
            COMPANY, acme, AutoTopUpIn(product="topup_50", threshold=500), ann
        )
        await auto_top_ups.start(checkout_data(acme, ann), sub)
        await ledger.reserve(
            COMPANY, acme, WELCOME_COMPANY - 1, f"candidate:{uuid.uuid4()}", Reason.CANDIDATE
        )
        await auto_top_ups.check(COMPANY, acme)
        # The charge's transaction.completed adds its credits, and they're used up again.
        await handle_completed(
            {
                "id": f"txn_{uuid.uuid4().hex[:12]}",
                "subscription_id": sub,
                "currency_code": "USD",
                "custom_data": None,
                "items": [{"price": {"id": "pri_50"}, "quantity": 1}],
                "details": {"totals": {"grand_total": "5000"}},
            }
        )
        wallet = await ledger.wallet(COMPANY, acme)
        await ledger.reserve(
            COMPANY,
            acme,
            wallet.balance - wallet.reserved - 1,
            f"candidate:{uuid.uuid4()}",
            Reason.CANDIDATE,
        )

        return await rows.claim_charge(COMPANY, acme, datetime.now(UTC) + AUTO_TOP_UP_COOLDOWN * 2)

    assert run(scenario()) is not None
