import uuid
from datetime import UTC, datetime

from app.constants.credits import CANDIDATE_CREDITS, WELCOME_COMPANY, Reason
from app.constants.products import TOP_UPS, OwnerType
from app.storage import ledger, purchases

NOW = datetime(2026, 10, 3, 12, tzinfo=UTC)
TOPUP = TOP_UPS[0]
TOPUP_CREDITS = 1_000
COMPANY = OwnerType.COMPANY


def company():
    return str(uuid.uuid4())


def test_a_candidate_is_charged_once_and_a_released_hold_comes_back(run):
    acme = company()

    async def scenario():
        await ledger.welcome_company(acme, f"{acme}@example.com")
        opened = await ledger.wallet(COMPANY, acme)
        held = await ledger.reserve(
            COMPANY, acme, CANDIDATE_CREDITS, "candidate:a", Reason.CANDIDATE
        )
        await ledger.reserve(COMPANY, acme, CANDIDATE_CREDITS, "candidate:b", Reason.CANDIDATE)
        await ledger.charge("candidate:a")
        await ledger.charge("candidate:a")
        await ledger.release("candidate:b")

        return opened, held, await ledger.wallet(COMPANY, acme)

    opened, held, done = run(scenario())

    assert (opened.balance, opened.reserved) == (WELCOME_COMPANY, 0)
    assert held is True
    assert (done.balance, done.reserved) == (WELCOME_COMPANY - CANDIDATE_CREDITS, 0)


def test_credits_set_aside_cant_be_held_twice(run):
    acme = company()

    async def scenario():
        await ledger.welcome_company(acme, f"{acme}@example.com")
        await ledger.reserve(COMPANY, acme, WELCOME_COMPANY, "candidate:all", Reason.CANDIDATE)

        return await ledger.reserve(COMPANY, acme, 1, "candidate:one-more", Reason.CANDIDATE)

    assert run(scenario()) is False


def test_a_retried_topup_is_granted_once(run):
    acme = company()

    async def scenario():
        args = (COMPANY, acme, TOPUP_CREDITS, 1, "txn", TOPUP.key, "ann", "1000")
        first = await purchases.grant(*args, "USD", NOW)
        again = await purchases.grant(*args, "USD", NOW)

        return first, again, (await ledger.wallet(COMPANY, acme)).balance

    assert run(scenario()) == (True, False, TOPUP_CREDITS)


def test_deleting_a_user_keeps_their_companys_purchases_without_them(run):
    acme, ann = company(), f"user-{uuid.uuid4()}"

    async def scenario():
        await purchases.grant(
            COMPANY, acme, TOPUP_CREDITS, 1, "txn2", TOPUP.key, ann, "1000", "USD", NOW
        )
        mine = await purchases.purchases_of(ann)
        await purchases.forget_buyer(ann)

        return mine, await purchases.purchases_of(ann), await purchases.for_transaction("txn2")

    mine, after, bought = run(scenario())

    assert [row.transaction_id for row in mine] == ["txn2"]
    assert after == []
    assert bought == (COMPANY, acme, TOPUP_CREDITS, "1000")


def test_a_new_company_by_the_same_person_doesnt_repeat_the_gift(run):
    email = f"user-{uuid.uuid4()}@Example.com"
    first, recreated = company(), company()

    async def scenario():
        assert await ledger.welcome_company(first, email)
        await purchases.delete_company(first)
        # The same Google account makes a new company.
        assert not await ledger.welcome_company(recreated, email.upper())

        return await ledger.wallet(COMPANY, recreated)

    assert run(scenario()).balance == 0


def test_a_refund_of_spent_credits_leaves_the_balance_negative(run):
    acme = company()

    async def scenario():
        await purchases.grant(
            COMPANY, acme, TOPUP_CREDITS, 1, "txn-r", TOPUP.key, "ann", "1000", "USD", NOW
        )
        await ledger.reserve(COMPANY, acme, 600, "candidate:spent", Reason.CANDIDATE)
        await ledger.charge("candidate:spent")
        await ledger.adjust(COMPANY, acme, -1_000, "adjustment:r1", Reason.REFUND)
        # Paddle sends the same event again.
        await ledger.adjust(COMPANY, acme, -1_000, "adjustment:r1", Reason.REFUND)
        blocked = await ledger.reserve(COMPANY, acme, 1, "candidate:after", Reason.CANDIDATE)

        return (await ledger.wallet(COMPANY, acme)).balance, blocked

    assert run(scenario()) == (-600, False)
