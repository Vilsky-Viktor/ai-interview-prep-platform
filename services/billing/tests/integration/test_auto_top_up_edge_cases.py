import uuid
from datetime import UTC, datetime

from app.constants.credits import WELCOME_COMPANY, Reason
from app.constants.products import AUTO_TOP_UP_RETRY_AFTER, OwnerType
from app.schemas.billing import AutoTopUpIn
from app.services import auto_top_ups
from app.storage import auto_top_ups as rows
from app.storage import ledger

COMPANY = OwnerType.COMPANY
CHOICE = AutoTopUpIn(product="topup_30", threshold=300)


def checkout_data(owner_id, buyer_id):
    return {"owner_type": COMPANY, "owner_id": owner_id, "buyer_id": buyer_id, "auto_top_up": "1"}


def test_a_second_member_turning_it_on_before_the_first_checkout_starts_it_with_their_card(
    run, paddle_calls
):
    ann, bob = f"user-{uuid.uuid4()}", f"user-{uuid.uuid4()}"
    acme = str(uuid.uuid4())
    sub = f"sub_{uuid.uuid4().hex[:12]}"

    async def scenario():
        await auto_top_ups.turn_on(COMPANY, acme, CHOICE, ann)
        waiting = await auto_top_ups.turn_on(COMPANY, acme, CHOICE, bob)
        await auto_top_ups.start(checkout_data(acme, bob), sub)
        # Once running, Ann changing the choice keeps Bob's card.
        await auto_top_ups.turn_on(COMPANY, acme, CHOICE, ann)

        return waiting, await auto_top_ups.out(COMPANY, acme), await rows.get(COMPANY, acme)

    waiting, after, row = run(scenario())

    assert waiting.checkout.custom_data["buyer_id"] == bob
    assert after.on
    assert row.buyer_id == bob
    assert paddle_calls == []


def test_a_subscription_that_ended_before_its_checkout_arrived_isnt_started(run, paddle_calls):
    ann = f"user-{uuid.uuid4()}"
    acme = str(uuid.uuid4())
    sub = f"sub_ended_{uuid.uuid4().hex[:12]}"

    async def scenario():
        await auto_top_ups.turn_on(COMPANY, acme, CHOICE, ann)
        # subscription.canceled came first and found nothing to turn off.
        await auto_top_ups.ended(sub)
        await auto_top_ups.start(checkout_data(acme, ann), sub)

        return await auto_top_ups.out(COMPANY, acme)

    after = run(scenario())

    assert not after.on and after.waiting


def test_a_declined_card_is_tried_again_only_after_a_day_or_a_new_save(run, paddle_calls):
    ann = f"user-{uuid.uuid4()}"
    acme = str(uuid.uuid4())
    sub = f"sub_declined_{uuid.uuid4().hex[:12]}"

    async def scenario():
        await ledger.welcome_company(acme, f"{acme}@example.com")
        await auto_top_ups.turn_on(COMPANY, acme, CHOICE, ann)
        await auto_top_ups.start(checkout_data(acme, ann), sub)
        await ledger.reserve(
            COMPANY, acme, WELCOME_COMPANY - 1, f"candidate:{acme}", Reason.CANDIDATE
        )
        await auto_top_ups.check(COMPANY, acme)
        soon = await rows.claim_charge(
            COMPANY, acme, datetime.now(UTC) + AUTO_TOP_UP_RETRY_AFTER / 2
        )
        next_day = await rows.claim_charge(
            COMPANY, acme, datetime.now(UTC) + AUTO_TOP_UP_RETRY_AFTER * 2
        )
        await auto_top_ups.turn_on(COMPANY, acme, CHOICE, ann)
        saved = await rows.get(COMPANY, acme)

        return soon, next_day, saved

    soon, next_day, saved = run(scenario())

    assert [call[0] for call in paddle_calls] == ["charge"]
    assert soon is None
    assert next_day is not None
    assert saved.failed_at is None
