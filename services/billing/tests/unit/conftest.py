import pytest

from app.storage import ledger


@pytest.fixture(autouse=True)
def wallets_exist(monkeypatch):
    """Unit tests have no database: every owner's wallet exists unless a test says otherwise."""

    async def wallets(owner_type, owner_ids):
        return {owner_id: object() for owner_id in owner_ids}

    monkeypatch.setattr(ledger, "wallets", wallets)
