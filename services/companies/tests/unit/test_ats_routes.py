import uuid
from datetime import UTC, datetime

import pytest
from cryptography.fernet import Fernet
from prepza_common.auth import current_user
from prepza_common.user import User

from app.config.settings import settings
from app.helpers.encryption import decrypt
from app.integrations import workable
from app.main import app
from app.models.ats import AtsConnection
from app.models.companies import Company, Member
from app.models.interviews import Interview
from app.storage import ats, ats_candidates, companies, interviews

COMPANY_ID = uuid.uuid4()
OTHER_COMPANY = uuid.uuid4()
INTERVIEW_ID = uuid.uuid4()
JOBS = [{"id": "A1", "name": "Accountant"}]
STAGES = [{"id": "assessment", "name": "Assessment"}]


def sign_in(uid):
    app.dependency_overrides[current_user] = lambda: User(
        uid=uid, email=f"{uid}@example.com", email_verified=True
    )


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def key(monkeypatch):
    """Integrations set up: an encryption key."""
    value = Fernet.generate_key().decode()
    monkeypatch.setattr(settings, "ats_encryption_key", value)

    return value


@pytest.fixture
def stored(monkeypatch):
    """A company with an admin and a viewer, its ATS rows kept in memory, and Workable answering
    with one job and one stage for the token "good"."""
    company = Company(id=COMPANY_ID, name="Acme", created_at=datetime.now(UTC))
    company.members = [
        Member(company_id=COMPANY_ID, user_id="ann", invited_email="a@x.com", role="admin"),
        Member(company_id=COMPANY_ID, user_id="vic", invited_email="v@x.com", role="viewer"),
    ]
    rows = {"connection": None, "links": [], "subscriptions": [], "targets": []}

    async def get_company(company_id):
        return company if company_id == COMPANY_ID else None

    async def connect(company_id, provider, account, credentials, user_id, member_id=None):
        rows["connection"] = AtsConnection(
            member_id=member_id,
            id=uuid.uuid4(),
            company_id=company_id,
            provider=provider,
            account=account,
            credentials=credentials,
            status="connected",
            created_by=user_id,
            created_at=datetime.now(UTC),
        )

    async def connection(company_id, provider):
        return rows["connection"]

    async def connections(company_id):
        return [rows["connection"]] if rows["connection"] else []

    async def disconnect(company_id, provider):
        rows["connection"] = None

    async def add_link(connection_id, interview_id, job, stage):
        rows["links"].append((interview_id, job["id"], stage["id"]))

        return uuid.uuid4()

    async def set_subscription(link_id, subscription_id):
        rows["subscriptions"].append(subscription_id)

    async def subscriptions(company_id, link_id=None):
        return list(rows["subscriptions"])

    async def no_counts(company_id):
        return {}

    async def member_id(subdomain, token, email):
        return "member-1"

    async def subscribe(subdomain, token, target, job_id, stage_id):
        rows["targets"].append(target)

        return "sub-1"

    async def get_interview(interview_id):
        if interview_id == INTERVIEW_ID:
            return Interview(id=INTERVIEW_ID, company_id=COMPANY_ID, title="Accountant")

        return Interview(id=interview_id, company_id=OTHER_COMPANY, title="Theirs")

    async def check(subdomain, token):
        if token != "good":
            raise workable.KeyRejected

    async def jobs(subdomain, token):
        return JOBS

    async def stages(subdomain, token, job_id):
        return STAGES

    monkeypatch.setattr(companies, "get", get_company)
    monkeypatch.setattr(interviews, "get", get_interview)
    for name, fake in {
        "connect": connect,
        "connection": connection,
        "connections": connections,
        "disconnect": disconnect,
        "add_link": add_link,
        "set_subscription": set_subscription,
        "subscriptions": subscriptions,
    }.items():
        monkeypatch.setattr(ats, name, fake)
    monkeypatch.setattr(workable, "check", check)
    monkeypatch.setattr(workable, "jobs", jobs)
    monkeypatch.setattr(workable, "stages", stages)
    monkeypatch.setattr(workable, "member_id", member_id)
    monkeypatch.setattr(workable, "subscribe", subscribe)
    monkeypatch.setattr(ats_candidates, "counts", no_counts)

    return rows


def connect(client, token="good", account="acme.workable.com"):
    return client.put(
        f"/ats/workable?company_id={COMPANY_ID}", json={"account": account, "token": token}
    )


def test_without_an_encryption_key_integrations_are_off(client, stored, monkeypatch):
    monkeypatch.setattr(settings, "ats_encryption_key", "set-me")
    sign_in("ann")

    assert client.get(f"/ats?company_id={COMPANY_ID}").json()["available"] is False
    assert connect(client).status_code == 503


def test_an_admin_connects_and_the_key_is_kept_encrypted(client, stored, key):
    sign_in("ann")

    assert connect(client).status_code == 204

    saved = stored["connection"]
    assert saved.account == "acme"
    assert saved.member_id == "member-1"
    assert "good" not in saved.credentials
    assert decrypt(key, saved.credentials) == '{"subdomain": "acme", "token": "good"}'
    # Never the key itself.
    assert client.get(f"/ats?company_id={COMPANY_ID}").json()["connections"] == [
        {
            "provider": "workable",
            "account": "acme",
            "status": "connected",
            "created_at": saved.created_at.isoformat().replace("+00:00", "Z"),
        }
    ]


def test_a_refused_token_or_a_wrong_address_isnt_saved(client, stored, key):
    sign_in("ann")

    assert connect(client, token="bad").status_code == 400
    assert connect(client, account="not an address").status_code == 400
    assert stored["connection"] is None


def test_a_viewer_sees_the_connection_but_changes_nothing(client, stored, key):
    sign_in("ann")
    connect(client)
    sign_in("vic")

    assert client.get(f"/ats?company_id={COMPANY_ID}").status_code == 200
    assert connect(client).status_code == 403
    assert client.delete(f"/ats/workable?company_id={COMPANY_ID}").status_code == 403
    assert client.get(f"/ats/workable/jobs?company_id={COMPANY_ID}").status_code == 403


def test_a_job_links_to_one_of_the_companys_interviews(client, stored, key):
    sign_in("ann")
    connect(client)
    body = {"provider": "workable", "job_id": "A1", "stage_id": "assessment"}

    assert client.get(f"/ats/workable/jobs?company_id={COMPANY_ID}").json() == JOBS
    assert (
        client.post(
            f"/ats/links?company_id={COMPANY_ID}",
            json={**body, "interview_id": str(INTERVIEW_ID)},
        ).status_code
        == 201
    )
    assert stored["links"] == [(INTERVIEW_ID, "A1", "assessment")]
    # Workable notifies this link's own address, and the subscription is kept to cancel it.
    assert stored["targets"][0].startswith("http://localhost:8090/api/companies/webhooks/ats/")
    assert stored["subscriptions"] == ["sub-1"]
    # Another company's interview, or a job or stage Workable doesn't have, isn't linked.
    other = {**body, "interview_id": str(uuid.uuid4())}
    unknown = {**body, "stage_id": "offer", "interview_id": str(INTERVIEW_ID)}

    assert client.post(f"/ats/links?company_id={COMPANY_ID}", json=other).status_code == 404
    assert client.post(f"/ats/links?company_id={COMPANY_ID}", json=unknown).status_code == 404
    assert len(stored["links"]) == 1


def test_a_key_workable_stops_accepting_marks_the_connection_broken(
    client, stored, key, monkeypatch
):
    broken = []

    async def refuse(subdomain, token):
        raise workable.KeyRejected

    async def mark_broken(connection_id):
        broken.append(connection_id)

    monkeypatch.setattr(workable, "jobs", refuse)
    monkeypatch.setattr(ats, "mark_broken", mark_broken)
    sign_in("ann")
    connect(client)

    response = client.get(f"/ats/workable/jobs?company_id={COMPANY_ID}")

    assert response.status_code == 409
    assert broken == [stored["connection"].id]
