import pytest

from app.integrations import billing
from app.storage import accounts, audit, invites


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


@pytest.fixture(autouse=True)
def audited(monkeypatch):
    """The audit log, in memory: (company id, user id, action, target id) as recorded."""
    events = []

    async def record(company_id, user_id, action, target_id=None):
        events.append((company_id, user_id, action, target_id))

    monkeypatch.setattr(audit, "record", record)

    return events
