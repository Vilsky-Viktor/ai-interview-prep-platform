import uuid
from datetime import UTC, datetime
from types import SimpleNamespace

from prepza_common.service_auth import issue_token

from app.storage import email_reminders

TOKEN = issue_token("notifications", "companies", "test-secret-that-is-at-least-32-bytes")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
COMPANY_ID = uuid.uuid4()


def test_members_say_who_can_act_and_leave_out_pending_invites(client, monkeypatch):
    async def with_members(company_ids):
        return [
            SimpleNamespace(
                id=COMPANY_ID,
                name="Acme",
                members=[
                    SimpleNamespace(user_id="ann", role="owner"),
                    SimpleNamespace(user_id="vic", role="viewer"),
                    SimpleNamespace(user_id=None, role="admin"),
                ],
            )
        ]

    monkeypatch.setattr(email_reminders, "with_members", with_members)

    response = client.post(
        "/internal/companies/members", json={"company_ids": [str(COMPANY_ID)]}, headers=HEADERS
    )

    assert response.json() == {
        "companies": [
            {
                "id": str(COMPANY_ID),
                "name": "Acme",
                "members": [
                    {"user_id": "ann", "editor": True},
                    {"user_id": "vic", "editor": False},
                ],
            }
        ]
    }


def test_waiting_interviews_pass_the_windows_through(client, monkeypatch):
    calls = []
    row = SimpleNamespace(
        id=uuid.uuid4(),
        company_id=COMPANY_ID,
        title="Backend",
        generation_id=None,
        created_at=datetime(2026, 10, 1, tzinfo=UTC),
    )

    async def without_candidates(after, before):
        calls.append(("ready", after, before))

        return [row]

    async def being_generated(after, before):
        calls.append(("started", after, before))

        return []

    monkeypatch.setattr(email_reminders, "without_candidates", without_candidates)
    monkeypatch.setattr(email_reminders, "being_generated", being_generated)
    params = {
        "ready_after": "2026-09-28T08:00:00+00:00",
        "ready_before": "2026-10-05T08:00:00+00:00",
        "started_after": "2026-09-23T08:00:00+00:00",
        "started_before": "2026-10-07T08:00:00+00:00",
    }

    response = client.get("/internal/interviews/waiting", params=params, headers=HEADERS)

    assert response.status_code == 200
    assert response.json()["without_candidates"][0]["title"] == "Backend"
    assert response.json()["being_generated"] == []
    assert [call[0] for call in calls] == ["ready", "started"]
    assert calls[0][2] == datetime(2026, 10, 5, 8, tzinfo=UTC)


def test_these_routes_need_a_service_token(client):
    assert client.post("/internal/companies/members", json={"company_ids": []}).status_code in (
        401,
        403,
    )
