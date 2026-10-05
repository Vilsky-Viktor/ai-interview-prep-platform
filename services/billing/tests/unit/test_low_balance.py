from app.constants.credits import CANDIDATE_CREDITS
from app.helpers.wallets import balance_out
from app.models.billing import Wallet


def test_a_company_runs_low_when_the_next_candidate_isnt_covered():
    short = CANDIDATE_CREDITS - 2
    covered = CANDIDATE_CREDITS

    assert balance_out(Wallet(owner_type="company", owner_id="acme", balance=short, reserved=0)).low
    assert not balance_out(
        Wallet(owner_type="company", owner_id="acme", balance=covered + 600, reserved=600)
    ).low
