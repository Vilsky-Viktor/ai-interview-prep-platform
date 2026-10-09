from types import SimpleNamespace

from app.constants.credits import CANDIDATE_CREDITS
from app.service_auth import service_token
from app.services import auto_top_ups
from app.storage import ledger, purchases

AUTH = {"Authorization": f"Bearer {service_token('billing')}"}
HOLD = {"company_id": "acme", "key": "session-1"}


def test_a_candidate_without_enough_credits_is_refused_with_a_message(client, monkeypatch):
    async def too_low(owner_type, owner_id, amount, key, reason):
        return False

    monkeypatch.setattr(ledger, "reserve", too_low)

    response = client.post("/internal/candidates/hold", params=HOLD, headers=AUTH)

    assert response.status_code == 402
    assert response.json() == {"detail": "Not enough credits. Top up to continue."}


def test_a_candidate_holds_its_credits(client, monkeypatch):
    held = []

    async def reserve(owner_type, owner_id, amount, key, reason):
        held.append((owner_id, amount, key))

        return True

    monkeypatch.setattr(ledger, "reserve", reserve)

    response = client.post("/internal/candidates/hold", params=HOLD, headers=AUTH)

    assert response.status_code == 204
    assert held == [("acme", CANDIDATE_CREDITS, "candidate:session-1")]


def test_internal_routes_need_a_service_token(client):
    assert client.post("/internal/candidates/hold", params=HOLD).status_code == 401


def test_several_companies_balances_at_once(client, monkeypatch):
    async def found(owner_type, owner_ids):
        return {"a": SimpleNamespace(owner_type="company", balance=900, reserved=300)}

    monkeypatch.setattr(ledger, "wallets", found)

    response = client.post(
        "/internal/companies/credits", json={"owner_ids": ["a", "b"]}, headers=AUTH
    )

    assert response.json() == {
        "a": {"balance": 900, "reserved": 300, "available": 600, "low": False, "candidates": 2},
        "b": {"balance": 0, "reserved": 0, "available": 0, "low": True, "candidates": 0},
    }


def test_a_removed_members_card_turns_off_only_their_auto_top_up(client, monkeypatch):
    calls = []

    async def turn_off(owner_type, owner_id, buyer_id=None):
        calls.append((owner_type, owner_id, buyer_id))

    monkeypatch.setattr(auto_top_ups, "turn_off", turn_off)

    response = client.delete(
        "/internal/companies/acme/auto-top-up", params={"buyer_id": "ann"}, headers=AUTH
    )

    assert response.status_code == 204
    assert calls == [("company", "acme", "ann")]


def test_library_exports_a_users_purchases_with_a_post(client, monkeypatch):
    """The export is a POST, like every service's, so library sends nothing in the URL."""

    async def purchases_of(user_id):
        return []

    monkeypatch.setattr(purchases, "purchases_of", purchases_of)

    response = client.post("/internal/users/ann/export", headers=AUTH)

    assert response.json() == {"purchases": []}


def test_low_companies_say_how_many_credits_are_available(client, monkeypatch):
    async def running_low(owner_type):
        return [SimpleNamespace(owner_id="acme", balance=400, reserved=300)]

    monkeypatch.setattr(ledger, "running_low", running_low)

    response = client.get("/internal/companies/low", headers=AUTH)

    assert response.json() == {"companies": [{"company_id": "acme", "available": 100}]}
