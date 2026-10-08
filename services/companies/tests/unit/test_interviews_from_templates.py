import uuid
from datetime import UTC, datetime

import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

from app.integrations import library
from app.main import app
from app.models.companies import Company, Member
from app.models.interviews import Interview
from app.storage import companies, interviews

COMPANY_ID = uuid.uuid4()
TEMPLATE_ID = uuid.uuid4()
SET_ID = uuid.uuid4()


@pytest.fixture
def setup(monkeypatch):
    """Bob, a member of the company; library copies TEMPLATE_ID only. Returns the tests made."""
    made = []
    company = Company(id=COMPANY_ID, name="Acme", created_at=datetime.now(UTC))
    company.members = [
        Member(
            company_id=COMPANY_ID,
            user_id="bob",
            invited_email="bob@example.com",
            role="admin",
            created_at=datetime.now(UTC),
        )
    ]

    async def get_company(_company_id):
        return company if _company_id == COMPANY_ID else None

    async def copy(template_id, company_id):
        if template_id != TEMPLATE_ID:
            return None

        return {"id": str(SET_ID), "title": "Bookkeeper", "language": "de"}

    async def create(company_id, set_id, title, language):
        made.append((company_id, set_id, title, language))

        return Interview(
            pass_mark=70,
            id=uuid.uuid4(),
            company_id=company_id,
            generation_id=None,
            set_id=uuid.UUID(set_id),
            generation_failed=False,
            title=title,
            language=language,
            question_seconds=60,
            hired=False,
            link_token=None,
            created_at=datetime.now(UTC),
        )

    monkeypatch.setattr(companies, "get", get_company)
    monkeypatch.setattr(library, "copy_template", copy)
    monkeypatch.setattr(interviews, "create_from_template", create)
    app.dependency_overrides[current_user] = lambda: User(
        uid="bob", email="bob@example.com", email_verified=True
    )

    yield made

    app.dependency_overrides.clear()


def start(client, template_id=TEMPLATE_ID, company_id=COMPANY_ID):
    return client.post(
        f"/interviews/from-template?company_id={company_id}",
        json={"template_id": str(template_id)},
    )


def test_a_template_becomes_a_ready_test_with_no_generation(client, setup):
    response = start(client)

    assert response.status_code == 201
    assert response.json()["generation_id"] is None
    assert response.json()["set_id"] == str(SET_ID)
    assert response.json()["title"] == "Bookkeeper"
    assert setup == [(COMPANY_ID, str(SET_ID), "Bookkeeper", "de")]


def test_an_unknown_template_or_another_company_is_not_found(client, setup):
    assert start(client, template_id=uuid.uuid4()).status_code == 404
    assert start(client, company_id=uuid.uuid4()).status_code == 404
    assert setup == []
