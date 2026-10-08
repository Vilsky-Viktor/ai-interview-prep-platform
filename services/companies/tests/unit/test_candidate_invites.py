import uuid
from datetime import UTC, datetime

from fastapi import HTTPException
from prepza_common.auth import current_user
from prepza_common.user import User

from app.integrations import billing
from app.main import app
from app.models.companies import Company, Member
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.services import candidate_invites
from app.services import outbox as outbox_service
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
        set_id=uuid.uuid4(),
        title="Backend interview",
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
    invited = set()
    used = []

    async def fake_interview(_interview_id):
        return interview

    async def fake_company(_company_id):
        return company

    async def fake_upsert(
        _interview_id, email, title, company, language, logo_path=None, hold_key=None
    ):
        # A new invite keeps the key its credits were set aside under.
        invite.hold_key = invite.hold_key or hold_key
        # The storage saves the email's event in the invite's transaction.
        sent.append(email)
        invited.add(email)

        return invite, False

    async def fake_status(_interview_id, email):
        return (await fake_held(_interview_id, email))[0]

    async def fake_held(_interview_id, email):
        return ("invited", invite.hold_key) if email in invited else (None, None)

    async def fake_hold(company_id, key):
        # Billing sets credits aside once per key, however often it's asked.
        if key not in used:
            used.append(key)

    async def no_flush():
        pass

    monkeypatch.setattr(interviews, "get", fake_interview)
    monkeypatch.setattr(companies, "get", fake_company)
    monkeypatch.setattr(invites, "upsert", fake_upsert)
    monkeypatch.setattr(invites, "held", fake_held)
    monkeypatch.setattr(invites, "status_of", fake_status)
    monkeypatch.setattr(billing, "hold_candidate", fake_hold)
    monkeypatch.setattr(outbox_service, "flush_quietly", no_flush)
    redis = FakeRedis()
    monkeypatch.setattr(candidate_invites, "get_redis", lambda: redis)

    return sent, used


URL = f"/interviews/{INTERVIEW_ID}/candidates"


def test_inviting_the_same_email_again_resends_the_invite(client, monkeypatch):
    sent, used = invite_setup(monkeypatch)
    url = URL

    first = client.post(url, json={"email": "Carol@example.com"})
    second = client.post(url, json={"email": "carol@example.com"})

    assert first.status_code == second.status_code == 201
    # Credits are set aside once for the candidate; the resend costs nothing more.
    # Set aside once, under the invite's own key.
    assert len(used) == 1
    assert used[0].startswith(f"{INTERVIEW_ID}:carol@example.com:")
    assert first.json()["id"] == second.json()["id"]
    assert sent == ["carol@example.com", "carol@example.com"]

    app.dependency_overrides.clear()


def test_one_address_gets_at_most_three_invites_a_day(client, monkeypatch):
    sent, _ = invite_setup(monkeypatch)

    codes = [client.post(URL, json={"email": "carol@example.com"}).status_code for _ in range(4)]
    other = client.post(URL, json={"email": "dave@example.com"})
    app.dependency_overrides.clear()

    assert codes == [201, 201, 201, 429]
    assert other.status_code == 201
    assert len(sent) == 4


def test_a_company_without_credits_cannot_invite_new_candidates(client, monkeypatch):
    sent, _ = invite_setup(monkeypatch)

    async def no_credits(company_id, key):
        raise HTTPException(402, "No candidate credits left.")

    monkeypatch.setattr(billing, "hold_candidate", no_credits)

    response = client.post(URL, json={"email": "erin@example.com"})
    app.dependency_overrides.clear()

    assert response.status_code == 402
    assert response.json()["detail"] == "No candidate credits left."
    assert sent == []


def test_an_email_limit_refusal_sets_no_credits_aside(client, monkeypatch):
    _, used = invite_setup(monkeypatch)

    async def limited(*args):
        raise HTTPException(429, "Too many requests. Try again later.")

    monkeypatch.setattr(candidate_invites, "hit_emails", limited)

    response = client.post(URL, json={"email": "frank@example.com"})
    app.dependency_overrides.clear()

    assert response.status_code == 429
    assert used == []


def test_an_invite_that_expired_while_sent_again_has_its_credits_set_aside_again(
    client, monkeypatch
):
    """Expiry gave them back after the invite was read; otherwise it finishes uncharged."""
    _, used = invite_setup(monkeypatch)
    upsert = invites.upsert
    held = []

    async def revived(*args, **kwargs):
        invite, _ = await upsert(*args, **kwargs)

        return invite, True

    async def hold_again(invite, key):
        held.append(key)

    monkeypatch.setattr(invites, "upsert", revived)
    monkeypatch.setattr(candidate_invites, "hold_again", hold_again)

    response = client.post(URL, json={"email": "gina@example.com"})
    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert held == used
