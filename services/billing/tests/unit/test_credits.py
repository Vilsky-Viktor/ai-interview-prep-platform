import pytest

from app.helpers.credits import credits_for


@pytest.mark.parametrize(
    ("cents", "credits"),
    [
        (1_000, 1_000),
        (24_900, 24_900),
        # From $250: 50% more, so a candidate costs $2.
        (25_000, 37_500),
        (50_000, 75_000),
        # From $1,000: three times as many, so a candidate costs $1.
        (100_000, 300_000),
    ],
)
def test_one_rule_gives_every_amount_its_credits_and_bonus(cents, credits):
    assert credits_for(cents) == credits


def test_every_top_up_buys_whole_candidates_at_its_volume_price(client):
    products = client.get("/catalog").json()["products"]

    assert [(p["key"], p["candidates"], p["candidate_cents"]) for p in products] == [
        ("topup_30", 10, 300),
        ("topup_150", 50, 300),
        ("topup_250", 125, 200),
        ("topup_1000", 1_000, 100),
    ]


def test_a_candidate_costs_3_then_2_then_1_dollar_by_top_up_size(client):
    prices = client.get("/catalog").json()["candidate_prices"]

    assert prices == [
        {"from_dollars": 1, "cents": 300},
        {"from_dollars": 250, "cents": 200},
        {"from_dollars": 1000, "cents": 100},
    ]
