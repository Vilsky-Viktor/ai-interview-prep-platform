import uuid

from app.constants.credits import KIT_CREDITS, WELCOME_USER, Reason
from app.constants.products import OwnerType
from app.routers.internal import hold_kit
from app.storage import ledger

USER = OwnerType.USER


def user():
    return f"user-{uuid.uuid4()}"


async def hold(generation_id: str, user_id: str) -> bool:
    return (await hold_kit(generation_id, user_id, "generation")).free


def test_a_new_learner_gets_100_credits_and_one_free_kit_once_per_person(run):
    ann, again = user(), user()
    email = f"{ann}@example.com"

    async def scenario():
        await ledger.welcome_user(ann, email)
        await ledger.welcome_user(ann, email)
        # The same person signs up again with a new account.
        await ledger.welcome_user(again, email)

        return await ledger.wallet(USER, ann), await ledger.wallet(USER, again)

    first, second = run(scenario())

    assert (first.balance, first.free_kits) == (WELCOME_USER, 1)
    assert (second.balance, second.free_kits) == (0, 0)


def test_the_first_kit_is_free_once_and_the_next_one_holds_its_credits(run):
    ann = user()
    free_kit, paid_kit = str(uuid.uuid4()), str(uuid.uuid4())

    async def scenario():
        await ledger.welcome_user(ann, f"{ann}@example.com")
        first = await hold(free_kit, ann)
        # The generation service retries the same hold.
        repeated = await hold(free_kit, ann)
        await ledger.charge(f"kit:{free_kit}")
        charged = await ledger.wallet(USER, ann)
        await ledger.adjust(USER, ann, KIT_CREDITS, f"adjustment:{paid_kit}", Reason.TOPUP)
        next_kit = await hold(paid_kit, ann)
        held = await ledger.wallet(USER, ann)
        history = await ledger.history(USER, ann, 0, 10)

        return first, repeated, charged, next_kit, held, history

    first, repeated, charged, next_kit, held, history = run(scenario())

    assert (first, repeated, next_kit) == (True, True, False)
    assert (charged.balance, charged.reserved, charged.free_kits) == (WELCOME_USER, 0, 0)
    assert (held.reserved, held.free_kits) == (KIT_CREDITS, 0)
    # The free kit shows as a kit of 0 credits.
    assert (Reason.KIT, 0) in [(row.reason, row.amount) for row in history]


def test_releasing_a_free_kit_gives_it_back_once(run):
    ann = user()
    generation_id = str(uuid.uuid4())

    async def scenario():
        await ledger.welcome_user(ann, f"{ann}@example.com")
        await hold(generation_id, ann)
        await ledger.release(f"kit:{generation_id}")
        await ledger.release(f"kit:{generation_id}")
        released = await ledger.wallet(USER, ann)
        # Trying the same kit again uses the free kit again.
        retried = await hold(generation_id, ann)

        return released, retried, await ledger.wallet(USER, ann)

    released, retried, after = run(scenario())

    assert (released.balance, released.reserved, released.free_kits) == (WELCOME_USER, 0, 1)
    assert retried is True
    assert (after.reserved, after.free_kits) == (0, 0)
