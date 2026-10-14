import pytest

from app.helpers.credits import credits_for


@pytest.mark.parametrize(
    ("cents", "credits"),
    [
        # Under $200 a candidate (500 credits) costs $5: $1 buys 100 credits.
        (1_000, 1_000),
        (19_900, 19_900),
        # From $200, $4.
        (20_000, 25_000),
        # From $600, $3.
        (60_000, 100_000),
        # From $1,000, $2.
        (100_000, 250_000),
    ],
)
def test_one_rule_gives_every_amount_its_credits(cents, credits):
    assert credits_for(cents) == credits


def test_every_top_up_buys_whole_candidates_at_its_own_price(client):
    products = client.get("/catalog").json()["products"]

    assert [(p["key"], p["candidates"], p["candidate_cents"]) for p in products] == [
        ("topup_50", 10, 500),
        ("topup_200", 50, 400),
        ("topup_600", 200, 300),
        ("topup_1000", 500, 200),
    ]


def test_a_candidate_costs_5_then_4_then_3_then_2_dollars_by_top_up_size(client):
    prices = client.get("/catalog").json()["candidate_prices"]

    assert prices == [
        {"from_dollars": 1, "cents": 500},
        {"from_dollars": 200, "cents": 400},
        {"from_dollars": 600, "cents": 300},
        {"from_dollars": 1000, "cents": 200},
    ]


def test_the_catalog_gives_the_free_candidates_and_the_price_range(client):
    catalog = client.get("/catalog").json()

    assert catalog["free_candidates"] == 3
    assert (catalog["candidate_cents_min"], catalog["candidate_cents_max"]) == (200, 500)
