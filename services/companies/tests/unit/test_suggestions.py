import uuid
from datetime import UTC, datetime

import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

from app.integrations import library, rounds
from app.main import app
from app.models.companies import Company, Member
from app.models.interviews import Interview
from app.storage import companies, interviews, talents

COMPANY_ID = uuid.uuid4()
INTERVIEW_ID = uuid.uuid4()
TEMPLATE_ID = uuid.uuid4()


@pytest.fixture
def test_page(monkeypatch):
    interview = Interview(id=INTERVIEW_ID, company_id=COMPANY_ID, set_id=uuid.uuid4(), pass_mark=70)
    interview.invites = []
    company = Company(id=COMPANY_ID, name="Acme", created_at=datetime.now(UTC))
    company.members = [
        Member(company_id=COMPANY_ID, user_id="bob", invited_email="bob@example.com", role="admin")
    ]
    similar = [TEMPLATE_ID]

    async def fake_interview(_id):
        return interview

    async def fake_company(_id):
        return company

    async def fake_similar(set_id):
        return similar

    async def fake_suggestions(template_ids):
        return [
            {
                "name": "Ann",
                "url": "https://www.linkedin.com/in/ann",
                "grade": 90,
                "template_id": str(template_ids[0]),
            }
        ]

    monkeypatch.setattr(interviews, "get", fake_interview)
    monkeypatch.setattr(companies, "get", fake_company)
    monkeypatch.setattr(library, "similar_templates", fake_similar)
    hidden = set()

    async def fake_hidden(_id):
        return hidden

    async def fake_hide(_id, url):
        hidden.add(url)

    monkeypatch.setattr(rounds, "talent_suggestions", fake_suggestions)
    monkeypatch.setattr(talents, "hidden_urls", fake_hidden)
    monkeypatch.setattr(talents, "hide", fake_hide)

    yield similar

    app.dependency_overrides.clear()


def sign_in(uid):
    app.dependency_overrides[current_user] = lambda: User(
        uid=uid, email=f"{uid}@example.com", email_verified=True
    )


def test_members_see_name_link_and_grade_only(client, test_page):
    sign_in("bob")

    assert client.get(f"/interviews/{INTERVIEW_ID}/suggestions").json() == [
        {"name": "Ann", "url": "https://www.linkedin.com/in/ann", "grade": 90}
    ]


def test_no_similar_role_means_no_suggestions(client, test_page):
    sign_in("bob")
    test_page.clear()

    assert client.get(f"/interviews/{INTERVIEW_ID}/suggestions").json() == []


def test_others_cant_see_a_companys_suggestions(client, test_page):
    sign_in("mallory")

    assert client.get(f"/interviews/{INTERVIEW_ID}/suggestions").status_code == 404


def test_a_hidden_talent_is_no_longer_suggested(client, test_page):
    sign_in("bob")
    url = "https://www.linkedin.com/in/ann"

    assert (
        client.post(f"/interviews/{INTERVIEW_ID}/suggestions/hide", json={"url": url}).status_code
        == 204
    )
    assert client.get(f"/interviews/{INTERVIEW_ID}/suggestions").json() == []


def test_others_cant_hide_a_companys_suggestions(client, test_page):
    sign_in("mallory")
    url = "https://www.linkedin.com/in/ann"

    assert (
        client.post(f"/interviews/{INTERVIEW_ID}/suggestions/hide", json={"url": url}).status_code
        == 404
    )
