import uuid
from datetime import UTC, datetime

import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

from app.helpers.verification import email_on_domain, website_domain
from app.main import app
from app.models.companies import Company, Member
from app.storage import companies, interviews

COMPANY_ID = uuid.uuid4()
URL = f"/companies/{COMPANY_ID}/website"


@pytest.fixture
def company(monkeypatch):
    found = Company(id=COMPANY_ID, name="Acme", created_at=datetime.now(UTC))
    found.members = [
        Member(company_id=COMPANY_ID, user_id="ann", invited_email="a@x.com", role="owner"),
        Member(company_id=COMPANY_ID, user_id="bob", invited_email="b@x.com", role="admin"),
    ]

    async def fake_get(_id):
        return found

    async def fake_set(_id, domain, verified):
        found.website_domain = domain
        found.verified_domain = domain if verified else None

    async def no_counts(ids):
        return {}

    monkeypatch.setattr(companies, "get", fake_get)
    monkeypatch.setattr(companies, "set_website", fake_set)
    monkeypatch.setattr(interviews, "counts", no_counts)

    yield found

    app.dependency_overrides.clear()


def sign_in(uid, email, verified=True):
    app.dependency_overrides[current_user] = lambda: User(
        uid=uid, email=email, email_verified=verified
    )


def test_a_website_is_read_as_its_domain():
    assert website_domain("https://www.Acme.com/jobs?x=1") == "acme.com"
    assert website_domain("acme.co.uk") == "acme.co.uk"
    assert website_domain("not a site") is None
    assert email_on_domain("ann@eu.acme.com", "acme.com")
    assert not email_on_domain("ann@notacme.com", "acme.com")


def test_an_admin_with_a_work_email_on_the_domain_verifies_at_once(client, company):
    sign_in("ann", "ann@acme.com")

    result = client.put(URL, json={"website": "https://www.acme.com"}).json()

    assert result == {"website_domain": "acme.com", "verified_domain": "acme.com"}


def test_a_personal_email_leaves_it_unverified_until_a_work_one_opens_it(client, company):
    sign_in("ann", "ann@gmail.com")
    first = client.put(URL, json={"website": "acme.com"}).json()

    assert first == {"website_domain": "acme.com", "verified_domain": None}

    sign_in("bob", "bob@acme.com")
    opened = client.get(f"/companies/{COMPANY_ID}").json()

    assert opened["verified_domain"] == "acme.com"


def test_free_mail_and_unverified_emails_never_verify(client, company):
    sign_in("ann", "ann@gmail.com")

    assert client.put(URL, json={"website": "gmail.com"}).status_code == 422

    sign_in("ann", "ann@acme.com", verified=False)

    assert client.put(URL, json={"website": "acme.com"}).json()["verified_domain"] is None
