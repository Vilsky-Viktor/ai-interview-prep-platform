import uuid
from datetime import UTC, datetime, timedelta

from app.constants.products import DELETED_OWNER, FREE_CANDIDATES, PRODUCTS, OwnerType
from app.storage import wallets

PRODUCT = {product.key: product for product in PRODUCTS}
NOW = datetime(2026, 10, 2, 12, tzinfo=UTC)


def test_a_company_gets_its_free_candidates_then_needs_credits(run):
    company = str(uuid.uuid4())

    async def scenario():
        used = [await wallets.use_candidate(company) for _ in range(FREE_CANDIDATES + 1)]
        await wallets.grant(
            "txn_a", [(PRODUCT["candidates_10"], 1)], company, "ann", "5000", "USD", NOW
        )

        return used, await wallets.use_candidate(company), await wallets.company_credits(company)

    used, after_buying, left = run(scenario())

    assert used == [True] * FREE_CANDIDATES + [False]
    assert after_buying is True
    assert left == 9


def test_a_learner_uses_the_free_one_then_credits_and_a_pass_covers_everything(run):
    user = f"user-{uuid.uuid4()}"

    async def scenario():
        free = await wallets.use_generation(user, NOW)
        none_left = await wallets.use_generation(user, NOW)
        await wallets.grant("txn_b", [(PRODUCT["generations_3"], 1)], user, user, "500", "USD", NOW)
        credits = [await wallets.use_generation(user, NOW) for _ in range(4)]
        next_month = await wallets.use_generation(user, NOW + timedelta(days=31))
        await wallets.grant(
            "txn_c", [(PRODUCT["job_search_pass"], 1)], user, user, "2400", "USD", NOW
        )
        with_pass = [await wallets.use_generation(user, NOW) for _ in range(5)]
        later = NOW + timedelta(days=91)
        expired = [await wallets.use_generation(user, later) for _ in range(2)]

        return free, none_left, credits, next_month, with_pass, expired

    free, none_left, credits, next_month, with_pass, expired = run(scenario())

    assert (free, none_left) == (True, False)
    assert credits == [True, True, True, False]
    # A new month brings a new free one.
    assert next_month is True
    assert with_pass == [True] * 5
    # After 90 days the pass is over: that month's free one, then nothing.
    assert expired == [True, False]


def test_a_retried_webhook_grants_once(run):
    company = str(uuid.uuid4())
    line = [(PRODUCT["candidates_10"], 1)]

    async def scenario():
        first = await wallets.grant("txn_d", line, company, "ann", "5000", "USD", NOW)
        again = await wallets.grant("txn_d", line, company, "ann", "5000", "USD", NOW)

        return first, again, await wallets.company_credits(company)

    first, again, credits = run(scenario())

    assert (first, again) == (1, 0)
    assert credits == FREE_CANDIDATES + 10


def test_deleting_a_user_keeps_their_purchases_anonymously(run):
    user = f"user-{uuid.uuid4()}"

    async def scenario():
        await wallets.grant(
            "txn_e", [(PRODUCT["job_search_pass"], 1)], user, user, "2400", "USD", NOW
        )
        await wallets.delete_user(user)

        return await wallets.get(OwnerType.USER, user), await wallets.purchases_of(DELETED_OWNER)

    wallet, anonymous = run(scenario())

    assert wallet is None
    assert any(row.transaction_id == "txn_e" and row.buyer_id is None for row in anonymous)
