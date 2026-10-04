import uuid
from datetime import UTC, datetime

from app.constants.credits import (
    CANDIDATE_CREDITS,
    KIT_CREDITS,
    WELCOME_COMPANY,
    WELCOME_USER,
    Reason,
)
from app.constants.products import DELETED_OWNER, TOP_UPS, OwnerType
from app.storage import ledger, purchases

NOW = datetime(2026, 10, 3, 12, tzinfo=UTC)
TOPUP = TOP_UPS[0]
TOPUP_CREDITS = 1_000


def user():
    return f"user-{uuid.uuid4()}"


def test_a_learner_starts_with_a_welcome_gift_and_a_kit_is_charged_only_when_ready(run):
    ann = user()

    async def scenario():
        await ledger.welcome_user(ann, f"{ann}@example.com")
        opened = await ledger.wallet(OwnerType.USER, ann)
        await ledger.adjust(OwnerType.USER, ann, KIT_CREDITS, "adjustment:k1", Reason.TOPUP)
        held = await ledger.reserve(OwnerType.USER, ann, KIT_CREDITS, "kit:1", Reason.KIT)
        again = await ledger.reserve(OwnerType.USER, ann, KIT_CREDITS, "kit:2", Reason.KIT)
        await ledger.charge("kit:1")
        await ledger.charge("kit:1")
        await ledger.release("kit:2")
        done = await ledger.wallet(OwnerType.USER, ann)
        history = await ledger.history(OwnerType.USER, ann, 0, 10)

        return opened, held, again, done, history

    opened, held, again, done, history = run(scenario())

    assert (opened.balance, opened.reserved) == (WELCOME_USER, 0)
    assert (held, again) == (True, False)
    assert (done.balance, done.reserved) == (WELCOME_USER, 0)
    # A repeated charge counts once; the history holds the gift, the top-up and the kit.
    assert sorted((row.reason, row.amount) for row in history) == [
        (Reason.KIT, -KIT_CREDITS),
        (Reason.TOPUP, KIT_CREDITS),
        (Reason.WELCOME, WELCOME_USER),
    ]


def test_a_companys_first_wallet_gets_the_gift_and_a_candidate_hold_comes_back(run):
    owner = user()
    first = str(uuid.uuid4())
    second = str(uuid.uuid4())

    async def scenario():
        await ledger.welcome_company(first, f"{owner}@example.com")
        await ledger.welcome_company(second, f"{owner}@example.com")
        await ledger.reserve(
            OwnerType.COMPANY, first, CANDIDATE_CREDITS, "candidate:a", Reason.CANDIDATE
        )
        await ledger.release("candidate:a")

        return (
            await ledger.wallet(OwnerType.COMPANY, first),
            await ledger.wallet(OwnerType.COMPANY, second),
        )

    company, empty = run(scenario())

    assert (company.balance, company.reserved) == (WELCOME_COMPANY, 0)
    assert (empty.balance, empty.reserved) == (0, 0)


def test_a_certificate_pays_its_author_once_and_needs_the_credits(run):
    learner, author = user(), user()

    async def scenario():
        await ledger.welcome_user(learner, f"{learner}@example.com")
        await ledger.welcome_user(author, f"{author}@example.com")
        paid = await ledger.spend(
            OwnerType.USER,
            learner,
            100,
            "certificate:t1",
            Reason.CERTIFICATE,
            "Ledgers",
            (author, 20),
        )
        repeated = await ledger.spend(
            OwnerType.USER,
            learner,
            100,
            "certificate:t1",
            Reason.CERTIFICATE,
            "Ledgers",
            (author, 20),
        )
        too_much = await ledger.spend(OwnerType.USER, learner, 1_000, "x", Reason.CHAT)

        return (
            paid,
            repeated,
            too_much,
            await ledger.wallet(OwnerType.USER, learner),
            await ledger.wallet(OwnerType.USER, author),
        )

    paid, repeated, too_much, learner_wallet, author_wallet = run(scenario())

    assert (paid, repeated, too_much) == (True, True, False)
    assert learner_wallet.balance == WELCOME_USER - 100
    assert author_wallet.balance == WELCOME_USER + 20


def test_credits_set_aside_cant_be_spent_twice(run):
    ann = user()

    async def scenario():
        await ledger.welcome_user(ann, f"{ann}@example.com")
        await ledger.adjust(OwnerType.USER, ann, KIT_CREDITS, "adjustment:k3", Reason.TOPUP)
        await ledger.reserve(OwnerType.USER, ann, KIT_CREDITS, "kit:3", Reason.KIT)

        # One credit more than the kit left free: the welcome credits.
        return await ledger.spend(OwnerType.USER, ann, WELCOME_USER + 1, "chat:1", Reason.CHAT)

    assert run(scenario()) is False


def test_a_retried_topup_is_granted_once(run):
    company = str(uuid.uuid4())

    async def scenario():
        args = (OwnerType.COMPANY, company, TOPUP_CREDITS, 1, "txn", TOPUP.key, "ann", "1000")
        first = await purchases.grant(*args, "USD", NOW)
        again = await purchases.grant(*args, "USD", NOW)

        return first, again, (await ledger.wallet(OwnerType.COMPANY, company)).balance

    assert run(scenario()) == (True, False, TOPUP_CREDITS)


def test_deleting_a_user_keeps_their_purchases_anonymously(run):
    ann = user()

    async def scenario():
        await purchases.grant(
            OwnerType.USER, ann, TOPUP_CREDITS, 1, "txn2", TOPUP.key, ann, "1000", "USD", NOW
        )
        await purchases.delete_user(ann)

        return (
            await purchases.purchases_of(DELETED_OWNER),
            await ledger.history(OwnerType.USER, ann, 0, 10),
        )

    rows, history = run(scenario())

    assert any(row.transaction_id == "txn2" and row.buyer_id is None for row in rows)
    assert history == []


def test_signing_up_again_or_a_new_company_doesnt_repeat_the_gifts(run):
    first, again = user(), user()
    email = f"{first}@Example.com"
    company, recreated = str(uuid.uuid4()), str(uuid.uuid4())

    async def scenario():
        assert await ledger.welcome_user(first, email)
        await ledger.welcome_company(company, email)
        await purchases.delete_user(first)
        await purchases.delete_company(company)
        # The same Google account signs in again as a new user, and makes a new company.
        assert not await ledger.welcome_user(again, email.upper())
        await ledger.welcome_company(recreated, email)

        return (
            await ledger.wallet(OwnerType.USER, again),
            await ledger.wallet(OwnerType.COMPANY, recreated),
        )

    learner, new_company = run(scenario())

    assert (learner.balance, new_company.balance) == (0, 0)


def test_a_refund_of_spent_credits_leaves_the_balance_negative(run):
    ann = user()

    async def scenario():
        await purchases.grant(
            OwnerType.USER, ann, TOPUP_CREDITS, 1, "txn-r", TOPUP.key, ann, "1000", "USD", NOW
        )
        await ledger.spend(OwnerType.USER, ann, 600, "chat:spent", Reason.CHAT)
        bought = await purchases.for_transaction("txn-r")
        await ledger.adjust(OwnerType.USER, ann, -1_000, "adjustment:r1", Reason.REFUND)
        # Paddle sends the same event again.
        await ledger.adjust(OwnerType.USER, ann, -1_000, "adjustment:r1", Reason.REFUND)
        blocked = await ledger.spend(OwnerType.USER, ann, 1, "chat:after", Reason.CHAT)

        return bought, (await ledger.wallet(OwnerType.USER, ann)).balance, blocked

    bought, balance, blocked = run(scenario())

    assert bought == (OwnerType.USER, ann, TOPUP_CREDITS, "1000")
    assert balance == -600
    assert blocked is False
