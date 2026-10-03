import uuid
from datetime import UTC, datetime

import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

from app.integrations import billing
from app.main import app
from app.models.companies import Company, Member
from app.storage import companies, interviews

OWNED_ID = uuid.uuid4()
JOINED_ID = uuid.uuid4()


def sign_in(email="bob@example.com", uid="bob"):
    app.dependency_overrides[current_user] = lambda: User(
        uid=uid, email=email, email_verified=True, name="Bob"
    )


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def company(company_id, name, role):
    item = Company(id=company_id, name=name, created_at=datetime.now(UTC))
    item.members = [
        Member(
            company_id=company_id,
            user_id="bob",
            invited_email="bob@example.com",
            role=role,
            created_at=datetime.now(UTC),
        )
    ]

    return item


@pytest.fixture
def two_companies(monkeypatch):
    owned = company(OWNED_ID, "My company", "owner")
    joined = company(JOINED_ID, "Arcolabs", "admin")

    async def fake_list(user_id, offset, limit):
        return [owned, joined]

    async def fake_get(company_id):
        if company_id == OWNED_ID:
            return owned

        if company_id == JOINED_ID:
            return joined

        return None

    async def fake_counts(company_ids):
        return {OWNED_ID: 3}

    monkeypatch.setattr(companies, "list_for_user", fake_list)
    monkeypatch.setattr(companies, "get", fake_get)
    monkeypatch.setattr(interviews, "counts", fake_counts)


def test_lists_every_membership(client, two_companies):
    sign_in()
    response = client.get("/companies")

    assert response.status_code == 200
    assert [(row["name"], row["role"], row["interview_count"]) for row in response.json()] == [
        ("My company", "owner", 3),
        ("Arcolabs", "admin", 0),
    ]


def test_opens_joined_company(client, two_companies):
    sign_in()
    response = client.get(f"/companies/{JOINED_ID}")

    assert response.status_code == 200
    assert response.json()["name"] == "Arcolabs"
    assert response.json()["role"] == "admin"


def test_unknown_company_is_hidden(client, two_companies):
    sign_in()

    assert client.get(f"/companies/{uuid.uuid4()}").status_code == 404


def test_owner_removes_company(client, two_companies, monkeypatch):
    removed = []

    async def fake_delete(company_id):
        removed.append(company_id)

    async def no_interviews(_company_id):
        return []

    monkeypatch.setattr(companies, "delete", fake_delete)
    monkeypatch.setattr(interviews, "list_for_company", no_interviews)
    sign_in()
    response = client.delete(f"/companies/{OWNED_ID}")

    assert response.status_code == 204
    assert removed == [OWNED_ID]


def test_admin_cannot_remove_company(client, two_companies):
    sign_in()

    assert client.delete(f"/companies/{JOINED_ID}").status_code == 403


def test_lists_the_users_companies_with_their_credits(client, monkeypatch):
    company = Company(id=uuid.uuid4(), name="Acme", created_at=datetime.now(UTC), members=[])

    async def mine(user_id, offset, limit):
        return [company]

    async def credits(company_ids):
        return {
            str(company.id): {"balance": 1_400, "reserved": 200, "available": 1_200, "low": False}
        }

    monkeypatch.setattr(companies, "list_for_user", mine)
    monkeypatch.setattr(billing, "companies_credits", credits)
    sign_in()

    response = client.get("/companies/credits")

    assert response.status_code == 200
    assert response.json() == [
        {"id": str(company.id), "name": "Acme", "available": 1_200, "low": False}
    ]
