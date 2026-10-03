import pytest

from app.helpers.credits import credits_for


@pytest.mark.parametrize(
    ("cents", "credits"),
    [
        (1_000, 1_000),
        (9_900, 9_900),
        (10_000, 10_200),
        (12_000, 12_240),
        (25_000, 26_250),
        (50_000, 55_000),
    ],
)
def test_one_rule_gives_every_amount_its_credits_and_bonus(cents, credits):
    assert credits_for(cents) == credits


def test_a_custom_amount_is_quoted_within_its_range(client):
    assert client.get("/topups/quote", params={"dollars": 120}).json() == {
        "price_cents": 12_000,
        "credits": 12_240,
        "bonus_credits": 240,
    }
    assert client.get("/topups/quote", params={"dollars": 9}).status_code == 422
    assert client.get("/topups/quote", params={"dollars": 501}).status_code == 422
