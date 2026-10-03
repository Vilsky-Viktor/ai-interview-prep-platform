import pytest

from app.integrations import billing
from app.storage import accounts, invites


@pytest.fixture(autouse=True)
def no_billing_calls(monkeypatch):
    """Billing is another service; tests that care about its calls replace these."""

    async def nothing(*args, **kwargs):
        return None

    async def no_invites(user_id, email):
        return []

    for name in ("delete_company", "release_candidate", "charge_candidate", "welcome_company"):
        monkeypatch.setattr(billing, name, nothing)

    async def none_unfinished(interview_id):
        return []

    monkeypatch.setattr(accounts, "candidate_invites", no_invites)
    monkeypatch.setattr(invites, "unfinished", none_unfinished)
