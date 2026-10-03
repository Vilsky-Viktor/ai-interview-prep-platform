import uuid

from app.constants.credits import REFERRAL_REWARD, WELCOME_COMPANY, WELCOME_USER
from app.constants.products import OwnerType
from app.services.referrals import reward_after_top_up
from app.storage import ledger, purchases, referrals

USER_REWARD = REFERRAL_REWARD[OwnerType.USER]


def user():
    return f"user-{uuid.uuid4()}"


async def available(owner_type, owner_id):
    row = await ledger.wallet(owner_type, owner_id)

    return row.balance - row.reserved


def test_a_referral_pays_both_learners_once_on_their_first_top_up(run):
    ann, bob = user(), user()

    async def scenario():
        await ledger.welcome_user(ann, f"{ann}@example.com")
        code = await referrals.code_of(OwnerType.USER, ann)
        same_code = await referrals.code_of(OwnerType.USER, ann)
        await ledger.welcome_user(bob, f"{bob}@example.com")
        recorded = await referrals.record(code, OwnerType.USER, bob, [])
        # The smallest top-up pays both, and only once.
        await reward_after_top_up(OwnerType.USER, bob, 1_000)
        await reward_after_top_up(OwnerType.USER, bob, 5_000)

        return (
            code == same_code,
            recorded,
            await available(OwnerType.USER, ann),
            await available(OwnerType.USER, bob),
            await referrals.rewarded_count(OwnerType.USER, ann),
        )

    same, recorded, ann_credits, bob_credits, count = run(scenario())

    assert same and recorded
    assert ann_credits == bob_credits == WELCOME_USER + USER_REWARD
    assert count == 1


def test_own_codes_other_kinds_related_companies_and_unknown_codes_refer_nobody(run):
    ann = user()
    acme, sister, other = (str(uuid.uuid4()) for _ in range(3))

    async def scenario():
        mine = await referrals.code_of(OwnerType.USER, ann)
        acme_code = await referrals.code_of(OwnerType.COMPANY, acme)

        return (
            await referrals.record(mine, OwnerType.USER, ann, []),
            await referrals.record(mine, OwnerType.COMPANY, other, []),
            await referrals.record(acme_code, OwnerType.COMPANY, sister, [acme]),
            await referrals.record("nope", OwnerType.USER, user(), []),
            await referrals.record(acme_code, OwnerType.COMPANY, other, []),
        )

    assert run(scenario()) == (False, False, False, False, True)


def test_a_deleted_referrer_leaves_the_new_company_its_own_reward(run):
    acme, newco = str(uuid.uuid4()), str(uuid.uuid4())

    async def scenario():
        await ledger.welcome_company(newco, f"{newco}@example.com")
        code = await referrals.code_of(OwnerType.COMPANY, acme)
        await referrals.record(code, OwnerType.COMPANY, newco, [])
        await purchases.delete_company(acme)
        # A company's $10 top-up isn't enough; $25 is.
        await reward_after_top_up(OwnerType.COMPANY, newco, 1_000)
        small = await available(OwnerType.COMPANY, newco)
        await reward_after_top_up(OwnerType.COMPANY, newco, 2_500)

        return (
            small,
            await available(OwnerType.COMPANY, newco),
            await ledger.wallets(OwnerType.COMPANY, [acme]),
        )

    small, credits, gone = run(scenario())

    assert small == WELCOME_COMPANY
    assert credits == WELCOME_COMPANY + REFERRAL_REWARD[OwnerType.COMPANY]
    assert gone == {}
