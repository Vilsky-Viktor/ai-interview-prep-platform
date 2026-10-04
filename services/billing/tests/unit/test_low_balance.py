from app.helpers.wallets import balance_out
from app.models.billing import Wallet


def test_a_learner_runs_low_under_100_credits():
    assert balance_out(
        Wallet(owner_type="user", owner_id="ann", balance=250, free_kits=0, reserved=200)
    ).low
    assert not balance_out(
        Wallet(owner_type="user", owner_id="ann", balance=100, free_kits=0, reserved=0)
    ).low


def test_a_company_runs_low_when_the_next_candidate_isnt_covered():
    assert balance_out(
        Wallet(owner_type="company", owner_id="acme", balance=398, free_kits=0, reserved=0)
    ).low
    assert not balance_out(
        Wallet(owner_type="company", owner_id="acme", balance=1_000, free_kits=0, reserved=600)
    ).low
