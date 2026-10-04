from types import SimpleNamespace

from app.service_auth import service_token
from app.storage import ledger

AUTH = {"Authorization": f"Bearer {service_token('billing')}"}


def test_a_kit_without_enough_credits_is_refused_with_a_message(client, monkeypatch):
    async def none(user_id, key):
        return False

    async def too_low(owner_type, owner_id, amount, key, reason):
        return False

    monkeypatch.setattr(ledger, "reserve_free_kit", none)
    monkeypatch.setattr(ledger, "reserve", too_low)

    response = client.post("/internal/kits/gen-1/hold", params={"user_id": "ann"}, headers=AUTH)

    assert response.status_code == 402
    assert response.json() == {"detail": "Not enough credits. Top up to continue."}


def test_a_free_kit_holds_no_credits_and_says_so(client, monkeypatch):
    held = []

    async def free(user_id, key):
        return True

    async def reserve(owner_type, owner_id, amount, key, reason):
        held.append(key)

        return True

    monkeypatch.setattr(ledger, "reserve_free_kit", free)
    monkeypatch.setattr(ledger, "reserve", reserve)

    response = client.post("/internal/kits/gen-1/hold", params={"user_id": "ann"}, headers=AUTH)

    assert response.status_code == 200
    assert response.json() == {"free": True}
    assert held == []


def test_a_certificate_on_a_public_kit_shares_with_its_author(client, monkeypatch):
    spent = []

    async def fake_spend(owner_type, owner_id, amount, key, reason, note=None, share=None):
        spent.append((owner_id, amount, key, reason, note, share))

        return True

    monkeypatch.setattr(ledger, "spend", fake_spend)

    response = client.post(
        "/internal/certificates",
        json={"owner_id": "ann", "key": "topic-1", "note": "Ledgers", "author_id": "bob"},
        headers=AUTH,
    )

    assert response.status_code == 204
    assert spent == [("ann", 100, "certificate:topic-1", "certificate", "Ledgers", ("bob", 20))]


def test_a_paid_chat_turn_costs_one_credit(client, monkeypatch):
    spent = []

    async def fake_spend(owner_type, owner_id, amount, key, reason, note=None, share=None):
        spent.append((owner_id, amount, key))

        return len(spent) == 1

    monkeypatch.setattr(ledger, "spend", fake_spend)
    body = {"owner_id": "ann", "key": "answer-1:4"}

    first = client.post("/internal/chat-turns", json=body, headers=AUTH)
    broke = client.post("/internal/chat-turns", json=body, headers=AUTH)

    assert first.status_code == 204
    assert broke.status_code == 402
    assert spent[0] == ("ann", 1, "chat:answer-1:4")


def test_internal_routes_need_a_service_token(client):
    assert client.post("/internal/kits/gen-1/hold", params={"user_id": "ann"}).status_code == 401


def test_several_companies_balances_at_once(client, monkeypatch):
    async def found(owner_type, owner_ids):
        return {"a": SimpleNamespace(owner_type="company", balance=900, reserved=300, free_kits=0)}

    monkeypatch.setattr(ledger, "wallets", found)

    response = client.post(
        "/internal/companies/credits", json={"owner_ids": ["a", "b"]}, headers=AUTH
    )

    assert response.json() == {
        "a": {"balance": 900, "reserved": 300, "available": 600, "low": False, "free_kits": 0},
        "b": {"balance": 0, "reserved": 0, "available": 0, "low": True, "free_kits": 0},
    }
