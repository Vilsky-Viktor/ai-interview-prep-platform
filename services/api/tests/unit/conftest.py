import json
import socket
import uuid
from datetime import UTC, datetime
from types import SimpleNamespace

import httpx
import pytest
from fastapi import HTTPException
from prepza_common.auth import current_user
from prepza_common.encryption import encrypt
from prepza_common.user import User

from app import auth
from app.config.settings import settings
from app.integrations import companies
from app.main import app
from app.services import webhooks as delivery
from app.storage import keys, webhooks

COMPANY = uuid.UUID("11111111-1111-4111-8111-111111111111")
INTERVIEW = uuid.UUID("22222222-2222-4222-8222-222222222222")
CANDIDATE = uuid.UUID("33333333-3333-4333-8333-333333333333")
# A Fernet key for the tests only.
KEY = "Zm9vYmFyYmF6cXV4cXV1eGNvcmdlZ3JhdWx0Z2FycGw="


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
    """Web hooks set up, and no signed-in user unless a test signs one in."""
    monkeypatch.setattr(settings, "api_encryption_key", KEY)
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

    async def invite(interview_id, email, sender_id):
        if state["refuse"]:
            raise HTTPException(state["refuse"], "Refused")

        state["sent"].append((interview_id, email, sender_id))

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
    unless a test says so."""
    state = {"keys": [], "webhooks": [], "used": [], "limited": False}

    async def by_hash(hashed):
        return next((key for key in state["keys"] if key.hash == hashed), None)

    async def used(key_id):
        state["used"].append(key_id)

    async def add_key(company_id, name, shown, hashed, user_id, expires_at):
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

    async def count_keys(company_id):
        return sum(key.company_id == company_id for key in state["keys"])

    async def keys_of(company_id):
        return [key for key in state["keys"] if key.company_id == company_id]

    async def add_webhook(company_id, url, sealed, user_id):
        hook = SimpleNamespace(
            id=uuid.uuid4(),
            company_id=company_id,
            url=url,
            secret=sealed,
            created_by=user_id,
            created_at=datetime.now(UTC),
            failing=False,
        )
        state["webhooks"].append(hook)

        return hook

    async def count_webhooks(company_id):
        return sum(hook.company_id == company_id for hook in state["webhooks"])

    async def webhooks_of(company_id):
        return [hook for hook in state["webhooks"] if hook.company_id == company_id]

    async def hit(redis, key, limit, window, message="Too many requests. Try again later."):
        if state["limited"]:
            raise HTTPException(429, message)

    monkeypatch.setattr(keys, "by_hash", by_hash)
    monkeypatch.setattr(keys, "used", used)
    monkeypatch.setattr(keys, "add", add_key)
    monkeypatch.setattr(keys, "count", count_keys)
    monkeypatch.setattr(keys, "of_company", keys_of)
    monkeypatch.setattr(webhooks, "add", add_webhook)
    monkeypatch.setattr(webhooks, "count", count_webhooks)
    monkeypatch.setattr(webhooks, "of_company", webhooks_of)
    monkeypatch.setattr(auth, "hit", hit)

    return state


@pytest.fixture
def endpoints(monkeypatch, companies_api):
    """COMPANY's web hooks, what each endpoint got, which fail or don't resolve, which got which
    event, and the events kept for the retry job (by web hook and event)."""
    state = {
        "hooks": [],
        "posted": [],
        "failing": set(),
        "delivered": set(),
        "public": True,
        "unresolved": set(),
        "retries": {},
    }

    def hook(url, secret="whsec_a", maker="u1"):
        found = SimpleNamespace(
            id=uuid.uuid4(),
            company_id=COMPANY,
            url=url,
            secret=encrypt(KEY, secret),
            created_by=maker,
            failing=False,
        )
        state["hooks"].append(found)

        return found

    async def of_company(company_id):
        return state["hooks"] if company_id == COMPANY else []

    async def delivered(webhook_id, event_id):
        return (webhook_id, event_id) in state["delivered"]

    async def mark_delivered(webhook_id, event_id):
        state["delivered"].add((webhook_id, event_id))

    async def set_failing(webhook_id, failing):
        next(item for item in state["hooks"] if item.id == webhook_id).failing = failing

    async def post(url, body, signature):
        if url in state["failing"]:
            raise httpx.ConnectError("down")

        state["posted"].append((url, json.loads(body), signature))

    async def add_retry(webhook_id, event_id, body, next_at):
        state["retries"].setdefault(
            (webhook_id, event_id),
            SimpleNamespace(
                event_id=event_id,
                body=body,
                attempts=1,
                next_at=next_at,
                created_at=datetime.now(UTC),
            ),
        )

    async def claim(limit):
        now = datetime.now(UTC)
        hooks = {item.id: item for item in state["hooks"]}
        due = [
            (row, hooks[webhook_id])
            for (webhook_id, _), row in state["retries"].items()
            if row.next_at <= now
        ]

        return due[:limit]

    async def postpone(webhook_id, event_id, attempts, next_at):
        row = state["retries"][(webhook_id, event_id)]
        row.attempts, row.next_at = attempts, next_at

    async def remove_retry(webhook_id, event_id):
        state["retries"].pop((webhook_id, event_id))

    monkeypatch.setattr(delivery.webhooks, "of_company", of_company)
    monkeypatch.setattr(delivery.webhooks, "delivered", delivered)
    monkeypatch.setattr(delivery.webhooks, "mark_delivered", mark_delivered)
    monkeypatch.setattr(delivery.webhooks, "set_failing", set_failing)
    monkeypatch.setattr(delivery.endpoints, "post", post)
    monkeypatch.setattr(delivery.retries, "add", add_retry)
    monkeypatch.setattr(delivery.retries, "claim", claim)
    monkeypatch.setattr(delivery.retries, "postpone", postpone)
    monkeypatch.setattr(delivery.retries, "remove", remove_retry)
    monkeypatch.setattr(delivery, "public_address", lambda url: check(url, state))
    state["hook"] = hook

    return state


def check(url, state):
    """public_address, faked: an address in state["unresolved"] doesn't resolve."""
    if url in state["unresolved"]:
        raise socket.gaierror

    return state["public"]
