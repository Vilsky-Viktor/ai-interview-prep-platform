import uuid
from datetime import UTC, datetime

from prepza_common.service_auth import issue_token

from app.models.ats import AtsCandidate
from app.storage import ats_candidates

SECRET = "test-secret-that-is-at-least-32-bytes"


def headers(callee="ats"):
    return {"Authorization": f"Bearer {issue_token('library', callee, SECRET)}"}


def test_deleting_an_account_deletes_its_ats_candidates_by_email(client, monkeypatch):
    deleted = []

    async def delete_email(email):
        deleted.append(email)

    monkeypatch.setattr(ats_candidates, "delete_email", delete_email)
    url = "/internal/users/u-1?email=ann@example.com"

    assert client.delete(url, headers=headers()).status_code == 204
    assert deleted == ["ann@example.com"]


def test_an_export_lists_what_atss_sent_about_them(client, monkeypatch):
    interview_id = uuid.uuid4()
    at = datetime(2026, 1, 2, tzinfo=UTC)
    row = AtsCandidate(
        email="ann@example.com",
        interview_id=interview_id,
        status="invited",
        reported_at=None,
        created_at=at,
    )

    async def of_email(email):
        return [row] if email == "ann@example.com" else []

    monkeypatch.setattr(ats_candidates, "of_email", of_email)
    response = client.get("/internal/users/u-1/export?email=ann@example.com", headers=headers())

    assert response.json() == {
        "ats_candidates": [
            {
                "email": "ann@example.com",
                "interview_id": str(interview_id),
                "status": "invited",
                "results_sent_at": None,
                "at": "2026-01-02T00:00:00+00:00",
            }
        ]
    }


def test_only_services_signed_for_ats_get_in(client):
    url = "/internal/users/u-1/export?email=ann@example.com"

    assert client.get(url).status_code in (401, 403)
    assert client.get(url, headers=headers("billing")).status_code == 401
