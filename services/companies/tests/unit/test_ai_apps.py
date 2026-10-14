import uuid
from datetime import UTC, datetime

import pytest
from prepza_common.auth import current_user
from prepza_common.service_auth import issue_token
from prepza_common.user import User

from app.constants.ai_apps import AI_APPS_CHANGED_BY_APP, AI_APPS_OFF
from app.constants.audit import AuditAction
from app.main import app
from app.models.companies import Company, Member
from app.routers import companies as companies_router
from app.storage import audit, companies, interviews

SECRET = "test-secret-that-is-at-least-32-bytes"
COMPANY_ID = uuid.uuid4()


def via(name):
    return {"X-Assistant": issue_token(name, "companies", SECRET)}


@pytest.fixture
def company(monkeypatch):
    """Acme, with Bob its admin and Vic a viewer; signed in as Bob."""
    acme = Company(
        id=COMPANY_ID, name="Acme", created_at=datetime.now(UTC), verification_status="none"
    )
    acme.members = [
        Member(company_id=COMPANY_ID, user_id="bob", invited_email="bob@example.com", role="admin"),
        Member(
            company_id=COMPANY_ID, user_id="vic", invited_email="vic@example.com", role="viewer"
        ),
    ]
    recorded = []

    async def get(_id):
        return acme

    async def set_ai_apps(company_id, allowed):
        acme.ai_apps_off_at = None if allowed else datetime.now(UTC)

    async def record(company_id, user_id, action, target_id=None, via=None):
        recorded.append((user_id, action, via))

    async def counts(_ids):
        return {}

    async def verify_by_email(company, user):
        return None

    monkeypatch.setattr(companies, "get", get)
    monkeypatch.setattr(companies, "set_ai_apps", set_ai_apps)
    monkeypatch.setattr(audit, "record", record)
    monkeypatch.setattr(interviews, "counts", counts)
    monkeypatch.setattr(companies_router, "verify_by_email", verify_by_email)
    sign_in("bob")

    yield acme, recorded

    app.dependency_overrides.clear()


def sign_in(user_id):
    app.dependency_overrides[current_user] = lambda: User(
        uid=user_id, email=f"{user_id}@example.com", email_verified=True
    )


def test_an_admin_turns_ai_apps_off_and_they_read_nothing_more(client, company):
    _, recorded = company
    path = f"/companies/{COMPANY_ID}"

    assert client.get(path, headers=via("mcp")).json()["ai_apps_allowed"] is True
    assert client.put(f"{path}/ai-apps", json={"allowed": False}).status_code == 204
    assert recorded == [("bob", AuditAction.AI_APPS_CHANGED, None)]

    refused = client.get(path, headers=via("mcp"))

    assert refused.status_code == 403
    assert refused.json()["detail"] == AI_APPS_OFF
    # The app itself and the in-app assistant go on as before.
    assert client.get(path).json()["ai_apps_allowed"] is False
    assert client.get(path, headers=via("assistant")).status_code == 200


def test_only_an_owner_or_admin_in_prepza_itself_changes_it(client, company):
    path = f"/companies/{COMPANY_ID}/ai-apps"

    for name in ("mcp", "assistant"):
        refused = client.put(path, json={"allowed": True}, headers=via(name))

        assert refused.status_code == 403
        assert refused.json()["detail"] == AI_APPS_CHANGED_BY_APP

    sign_in("vic")

    assert client.put(path, json={"allowed": False}).status_code == 403
