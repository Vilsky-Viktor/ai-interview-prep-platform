import uuid
from datetime import UTC, datetime

import pytest
from prepza_common.audit_actions import AuditAction, TargetKind
from prepza_common.auth import current_user
from prepza_common.user import User

from app.main import app
from app.models.companies import Company, Member
from app.models.interviews import Interview
from app.storage import companies, interviews

COMPANY_ID = uuid.uuid4()
INTERVIEW_ID = uuid.uuid4()


def sign_in():
    app.dependency_overrides[current_user] = lambda: User(
        uid="bob", email="bob@example.com", email_verified=True, name="Bob"
    )


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def test_only_the_settings_sent_change(client, monkeypatch, audited):
    sign_in()
    saved = []
    # Not the defaults, so a reset to them would show.
    fields = {
        "id": INTERVIEW_ID,
        "company_id": COMPANY_ID,
        "generation_id": uuid.uuid4(),
        "set_id": None,
        "pass_mark": 85,
        "question_seconds": 30,
        "hired": False,
    }
    company = Company(id=COMPANY_ID, name="My company", created_at=datetime.now(UTC))
    company.members = [
        Member(
            company_id=COMPANY_ID,
            user_id="bob",
            invited_email="bob@example.com",
            role="owner",
            created_at=datetime.now(UTC),
        )
    ]

    async def fake_interview(_interview_id):
        # As read for each request, with what earlier ones saved.
        return Interview(**{**fields, **{k: v for item in saved for k, v in item.items()}})

    async def fake_company(_company_id):
        return company

    async def fake_update(_interview_id, settings):
        saved.append(settings.model_dump(exclude_none=True))

    monkeypatch.setattr(interviews, "get", fake_interview)
    monkeypatch.setattr(companies, "get", fake_company)
    monkeypatch.setattr(interviews, "update_settings", fake_update)
    url = f"/interviews/{INTERVIEW_ID}/settings"

    assert client.patch(url, json={"hired": True}).status_code == 204
    assert client.patch(url, json={"question_seconds": 45}).status_code == 204
    assert saved == [{"hired": True}, {"question_seconds": 45}]
    settings_changed = (
        COMPANY_ID,
        "bob",
        AuditAction.INTERVIEW_SETTINGS_CHANGED,
        INTERVIEW_ID,
        TargetKind.INTERVIEW,
    )
    # Each change is recorded; without a pass mark sent, nothing about it.
    assert audited == [settings_changed, settings_changed]

    client.patch(url, json={"question_seconds": 45, "hired": True, "pass_mark": 85})

    # The same settings and pass mark aren't a change.
    assert len(audited) == 2

    client.patch(url, json={"pass_mark": 80})

    assert audited[2:] == [
        (COMPANY_ID, "bob", AuditAction.PASS_MARK_CHANGED, INTERVIEW_ID, TargetKind.INTERVIEW)
    ]
    too_short = client.patch(url, json={"question_seconds": 5})

    assert too_short.status_code == 422


def test_a_tests_status_follows_its_candidates_and_the_hired_mark():
    from app.helpers.interviews import interview_status

    assert interview_status(False, 0) == "new"
    assert interview_status(False, 3) == "in_process"
    # Marked as hired wins, with or without candidates.
    assert interview_status(True, 3) == "hired"
    assert interview_status(True, 0) == "hired"
