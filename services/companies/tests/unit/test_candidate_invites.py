import uuid
from datetime import UTC, datetime

from prepza_common.auth import current_user
from prepza_common.user import User

from app.main import app
from app.models.companies import Company, Member
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.routers import interviews as interviews_router
from app.storage import companies, interviews, invites
from tests.unit.fake_redis import FakeRedis

COMPANY_ID = uuid.uuid4()
INTERVIEW_ID = uuid.uuid4()


def invite_setup(monkeypatch):
    """Signs in Bob, Acme's owner; returns the emails the published events would send."""
    app.dependency_overrides[current_user] = lambda: User(
        uid="bob", email="bob@example.com", email_verified=True, name="Bob"
    )
    interview = Interview(
        id=INTERVIEW_ID,
        company_id=COMPANY_ID,
        generation_id=uuid.uuid4(),
        share_results=False,
        set_id=uuid.uuid4(),
        title="Backend interview",
        invites=[],
    )
    company = Company(id=COMPANY_ID, name="Acme", created_at=datetime.now(UTC))
    company.members = [
        Member(company_id=COMPANY_ID, user_id="bob", invited_email="bob@example.com", role="owner")
    ]
    invite = CandidateInvite(
        id=uuid.uuid4(),
        interview_id=INTERVIEW_ID,
        email="carol@example.com",
        token="token",
        status="invited",
        created_at=datetime.now(UTC),
    )
    sent = []

    async def fake_interview(_interview_id):
        return interview

    async def fake_company(_company_id):
        return company

    async def fake_upsert(_interview_id, _email):
        return invite

    async def fake_publish(event_type, data):
        sent.append(data["email"])

    monkeypatch.setattr(interviews, "get", fake_interview)
    monkeypatch.setattr(companies, "get", fake_company)
    monkeypatch.setattr(invites, "upsert", fake_upsert)
    monkeypatch.setattr(interviews_router, "publish", fake_publish)
    redis = FakeRedis()
    monkeypatch.setattr(interviews_router, "get_redis", lambda: redis)

    return sent


URL = f"/interviews/{INTERVIEW_ID}/candidates"


def test_inviting_the_same_email_again_resends_the_invite(client, monkeypatch):
    sent = invite_setup(monkeypatch)
    url = URL

    first = client.post(url, json={"email": "Carol@example.com"})
    second = client.post(url, json={"email": "carol@example.com"})

    assert first.status_code == second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    assert sent == ["carol@example.com", "carol@example.com"]

    app.dependency_overrides.clear()


def test_one_address_gets_at_most_three_invites_a_day(client, monkeypatch):
    sent = invite_setup(monkeypatch)

    codes = [client.post(URL, json={"email": "carol@example.com"}).status_code for _ in range(4)]
    other = client.post(URL, json={"email": "dave@example.com"})
    app.dependency_overrides.clear()

    assert codes == [201, 201, 201, 429]
    assert other.status_code == 201
    assert len(sent) == 4
