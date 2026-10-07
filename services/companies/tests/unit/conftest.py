import pytest
from prepza_common import memory_cache

from app.integrations import billing
from app.storage import accounts, audit, candidates, invites
from tests.unit import fake_candidates


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


@pytest.fixture(autouse=True)
def stored_candidates(monkeypatch):
    """Candidates in memory (tests.unit.fake_candidates), emptied for each test."""
    fake_candidates.ROWS.clear()
    fake_candidates.SAVED.clear()

    for name in ("get", "counts", "any_finished", "unscored", "save_results", "for_report"):
        monkeypatch.setattr(candidates, name, getattr(fake_candidates, name))

    return fake_candidates


@pytest.fixture(autouse=True)
def nothing_cached(monkeypatch):
    """Library's answers kept in memory (services/set_cache.py) start empty for each test."""
    monkeypatch.setattr(memory_cache, "_entries", {})
