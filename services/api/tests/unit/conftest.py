import uuid
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from prepza_common import memory_cache
from prepza_common.auth import current_user
from prepza_common.user import User

from app import auth
from app.config.settings import settings
from app.integrations import companies
from app.main import app
from app.storage import keys, webhooks
from tests.unit.ids import CANDIDATE, COMPANY, INTERVIEW, KEY

# The web hook fakes, a fixture of their own module.
from tests.unit.webhook_fakes import endpoints  # noqa: F401


def interview(**changes) -> dict:
    """An interview as companies' internal API returns it."""
    return {
        "id": str(INTERVIEW),
        "title": "Backend",
        "status": "in_process",
        "set_id": str(uuid.uuid4()),
        "pass_mark": 70,
        "candidate_count": 1,
        "created_at": "2026-10-01T09:00:00Z",
        **changes,
    }


def candidate(**changes) -> dict:
    return {
        "id": str(CANDIDATE),
        "email": "anna@example.com",
        "name": "Anna Nowak",
        "status": "finished",
        "progress": 100,
        "grade": 86,
        "passed": True,
        "tab_leaves": 0,
        "copies": 1,
        "fast_answers": 0,
        "created_at": "2026-10-02T10:30:00Z",
        **changes,
    }


@pytest.fixture(autouse=True)
def configured(monkeypatch):
    """Web hooks set up, nothing remembered from another test, and no signed-in user unless a
    test signs one in."""
    monkeypatch.setattr(settings, "api_encryption_key", KEY)
    monkeypatch.setattr(memory_cache, "_entries", {})
    yield
    app.dependency_overrides.clear()


def sign_in(uid="u1"):
    app.dependency_overrides[current_user] = lambda: User(
        uid=uid, email=f"{uid}@example.com", email_verified=True, name="Ann"
    )


@pytest.fixture
def companies_api(monkeypatch):
    """The companies service, faked: roles by user in COMPANY, its one interview and candidate,
    the invites it sent, or the status it refuses them with."""
    state = {"roles": {"u1": "owner"}, "sent": [], "refuse": None, "missing": False}

    async def access(company_id, user_id):
        role = state["roles"].get(user_id) if company_id == COMPANY else None

        return {"member": role is not None, "editor": role in ("owner", "admin")}

    def ours(company_id, interview_id):
        if company_id != COMPANY or interview_id != INTERVIEW or state["missing"]:
            raise HTTPException(404, "Interview not found")

    async def interviews(company_id, offset, limit):
        return [interview()] if company_id == COMPANY else []

    async def get_interview(company_id, interview_id):
        ours(company_id, interview_id)

        return interview()

    async def candidates(company_id, interview_id, offset, limit):
        ours(company_id, interview_id)

        return [candidate()]

    async def get_candidate(company_id, interview_id, invite_id):
        ours(company_id, interview_id)

        return candidate(id=str(invite_id))

    async def invite(
        interview_id, email, sender_id, name=None, return_url=None, sign_in=True, theme=None
    ):
        if state["refuse"]:
            raise HTTPException(state["refuse"], "Refused")

        state["sent"].append((interview_id, email, sender_id))
        state.setdefault("names", {})[email] = name
        state.setdefault("options", {})[email] = (return_url, sign_in, theme)

        return CANDIDATE

    monkeypatch.setattr(companies, "access", access)
    monkeypatch.setattr(companies, "interviews", interviews)
    monkeypatch.setattr(companies, "interview", get_interview)
    monkeypatch.setattr(companies, "candidates", candidates)
    monkeypatch.setattr(companies, "candidate", get_candidate)
    monkeypatch.setattr(companies, "invite", invite)

    return state


@pytest.fixture
def stored(monkeypatch):
    """Keys and web hooks in memory instead of the database, and requests never rate limited
    unless a test says so (the rate counters asked for are in "counted")."""
    state = {"keys": [], "webhooks": [], "used": [], "limited": False, "counted": []}

    async def by_hash(hashed):
        return next((key for key in state["keys"] if key.hash == hashed), None)

    async def used(key_id):
        state["used"].append(key_id)

    async def add_key(company_id, name, shown, hashed, user_id, expires_at, limit):
        if sum(key.company_id == company_id for key in state["keys"]) >= limit:
            return None

        key = SimpleNamespace(
            id=uuid.uuid4(),
            company_id=company_id,
            name=name,
            shown=shown,
            hash=hashed,
            created_by=user_id,
            created_at=datetime.now(UTC),
            expires_at=expires_at,
            last_used_at=None,
        )
        state["keys"].append(key)

        return key

    async def keys_of(company_id):
        return [key for key in state["keys"] if key.company_id == company_id]

    async def add_webhook(company_id, url, sealed, user_id, limit):
        if sum(hook.company_id == company_id for hook in state["webhooks"]) >= limit:
            return None

        hook = SimpleNamespace(
            id=uuid.uuid4(),
            company_id=company_id,
            url=url,
            secret=sealed,
            created_by=user_id,
            created_at=datetime.now(UTC),
            failing=False,
            stopped=False,
        )
        state["webhooks"].append(hook)

        return hook

    async def webhooks_of(company_id):
        return [hook for hook in state["webhooks"] if hook.company_id == company_id]

    async def hit(redis, key, limit, window, message="Too many requests. Try again later."):
        state["counted"].append(key)

        if state["limited"]:
            raise HTTPException(429, message)

    monkeypatch.setattr(keys, "by_hash", by_hash)
    monkeypatch.setattr(keys, "used", used)
    monkeypatch.setattr(keys, "add", add_key)
    monkeypatch.setattr(keys, "of_company", keys_of)
    monkeypatch.setattr(webhooks, "add", add_webhook)
    monkeypatch.setattr(webhooks, "of_company", webhooks_of)
    monkeypatch.setattr(auth, "hit", hit)

    return state
