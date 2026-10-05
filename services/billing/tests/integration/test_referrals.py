import uuid

from app.constants.credits import REFERRAL_REWARD, WELCOME_COMPANY
from app.constants.products import OwnerType
from app.services.referrals import reward_after_top_up
from app.storage import ledger, purchases, referrals

COMPANY = OwnerType.COMPANY


def company():
    return str(uuid.uuid4())


async def available(owner_type, owner_id):
    row = await ledger.wallet(owner_type, owner_id)

    return row.balance - row.reserved


def test_a_referral_pays_both_companies_once_on_a_big_enough_top_up(run):
    acme, newco = company(), company()

    async def scenario():
        await ledger.welcome_company(acme, f"{acme}@example.com")
        code = await referrals.code_of(COMPANY, acme)
        same_code = await referrals.code_of(COMPANY, acme)
        await ledger.welcome_company(newco, f"{newco}@example.com")
        recorded = await referrals.record(code, COMPANY, newco, [])
        await reward_after_top_up(COMPANY, newco)
        await reward_after_top_up(COMPANY, newco)

        return (
            code == same_code,
            recorded,
            await available(COMPANY, acme),
            await available(COMPANY, newco),
            await referrals.rewarded_count(COMPANY, acme),
            [row.owner_id for row in await referrals.rewards(COMPANY, acme, 10)],
        )

    same, recorded, acme_credits, newco_credits, count, rewarded = run(scenario())

    assert same and recorded
    assert acme_credits == newco_credits == WELCOME_COMPANY + REFERRAL_REWARD
    assert count == 1
    assert rewarded == [newco]


def test_own_codes_related_companies_and_unknown_codes_refer_nobody(run):
    acme, sister, other = (company() for _ in range(3))

    async def scenario():
        acme_code = await referrals.code_of(COMPANY, acme)

        return (
            await referrals.record(acme_code, COMPANY, acme, []),
            await referrals.record(acme_code, COMPANY, sister, [acme]),
            await referrals.record("nope", COMPANY, other, []),
            await referrals.record(acme_code, COMPANY, other, []),
        )

    assert run(scenario()) == (False, False, False, True)


def test_a_deleted_referrer_leaves_the_new_company_its_own_reward(run):
    acme, newco = str(uuid.uuid4()), str(uuid.uuid4())

    async def scenario():
        await ledger.welcome_company(newco, f"{newco}@example.com")
        code = await referrals.code_of(OwnerType.COMPANY, acme)
        await referrals.record(code, OwnerType.COMPANY, newco, [])
        await purchases.delete_company(acme)
        await reward_after_top_up(OwnerType.COMPANY, newco)

        return (
            await available(OwnerType.COMPANY, newco),
            await ledger.wallets(OwnerType.COMPANY, [acme]),
        )

    credits, gone = run(scenario())

    assert credits == WELCOME_COMPANY + REFERRAL_REWARD
    assert gone == {}
