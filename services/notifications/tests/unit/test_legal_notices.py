import asyncio
from datetime import UTC, date, datetime, timedelta
from types import SimpleNamespace

import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

from app.constants.legal_notices import ALREADY_ASKED, TOO_LATE
from app.main import app
from app.services import delivery, legal_notices
from app.storage import legal_notices as notices_store
from app.storage import sent_emails

TODAY = datetime.now(UTC).date()
LATER = (TODAY + timedelta(days=20)).isoformat()
SOON = (TODAY + timedelta(days=3)).isoformat()


def person(user_id, language="en"):
    return {"user_id": user_id, "email": f"{user_id}@example.com", "language": language}


@pytest.fixture
def notices(monkeypatch):
    """The versions, the notices asked for, the recipients and delivery, faked."""
    state = SimpleNamespace(asked={}, sent=[], marked=[], claims=[])
    monkeypatch.setattr(
        legal_notices,
        "LEGAL_VERSIONS",
        {"terms": LATER, "privacy": SOON, "dpa": TODAY.isoformat()},
    )

    async def all_notices():
        return [
            SimpleNamespace(document=document, version=version, sent_at=sent_at)
            for (document, version), sent_at in state.asked.items()
        ]

    async def ask(document, version, user_id):
        if (document, version) in state.asked:
            return False

        state.asked[(document, version)] = None

        return True

    async def mark_sent(document, version):
        state.marked.append(document)
        state.asked[(document, version)] = datetime.now(UTC)

    async def user_ids():
        return ["ann", "bob"]

    async def editor_ids():
        return ["ann"]

    async def recipients(ids):
        return [person(user_id, "de" if user_id == "bob" else "en") for user_id in ids]

    async def claim(user_id, kind, today, every_days, items=()):
        state.claims.append((user_id, kind, list(items)))

        return list(items)

    async def send(email, key):
        state.sent.append(email)

    monkeypatch.setattr(notices_store, "all_notices", all_notices)
    monkeypatch.setattr(notices_store, "ask", ask)
    monkeypatch.setattr(notices_store, "sent", mark_sent)
    monkeypatch.setattr(legal_notices.library, "user_ids", user_ids)
    monkeypatch.setattr(legal_notices.library, "recipients", recipients)
    monkeypatch.setattr(legal_notices.companies, "editor_ids", editor_ids)
    monkeypatch.setattr(sent_emails, "claim", claim)
    monkeypatch.setattr(delivery, "send", send)

    async def no_wait(_seconds):
        return None

    monkeypatch.setattr("app.services.member_sends.asyncio.sleep", no_wait)

    return state


def states():
    return {item["document"]: item["state"] for item in asyncio.run(legal_notices.states())}


def test_a_notice_is_asked_for_once_and_at_least_14_days_ahead(notices):
    assert states() == {"terms": "sendable", "privacy": "too_late", "dpa": "in_force"}

    asyncio.run(legal_notices.ask("terms", "sam"))

    with pytest.raises(Exception) as again:
        asyncio.run(legal_notices.ask("terms", "sam"))

    with pytest.raises(Exception) as soon:
        asyncio.run(legal_notices.ask("privacy", "sam"))

    assert (again.value.detail, soon.value.detail) == (ALREADY_ASKED, TOO_LATE)
    assert states()["terms"] == "sending"


def test_the_terms_go_to_everyone_and_the_dpa_to_owners_and_admins_once(notices):
    legal_notices.LEGAL_VERSIONS["dpa"] = LATER
    asyncio.run(legal_notices.ask("terms", "sam"))
    asyncio.run(legal_notices.ask("dpa", "sam"))

    sent = asyncio.run(legal_notices.send_legal_notices(datetime.now(UTC)))

    assert sent == 3
    ann = sorted(email.subject for email in notices.sent if email.to == "ann@example.com")
    assert ann == [
        f"We're updating prepza's data processing agreement on {LATER}",
        f"We're updating prepza's terms on {LATER}",
    ]
    assert [email.to for email in notices.sent].count("bob@example.com") == 1
    # Each names its version, so nobody gets it twice.
    assert {(claim[1], *claim[2]) for claim in notices.claims} == {
        ("legal_terms", LATER),
        ("legal_dpa", LATER),
    }
    assert sorted(notices.marked) == ["dpa", "terms"]
    assert states()["terms"] == "sent"
    # A later run has nothing left to send.
    assert asyncio.run(legal_notices.send_legal_notices(datetime.now(UTC))) == 0


def test_only_a_superadmin_sees_and_asks_for_notices(client, notices, monkeypatch):
    monkeypatch.setenv("SUPERADMIN_EMAILS", "sam@prepza.dev")
    app.dependency_overrides[current_user] = lambda: User(
        uid="ann", email="ann@example.com", email_verified=True
    )

    assert client.get("/superadmin/legal-notices").status_code == 404

    app.dependency_overrides[current_user] = lambda: User(
        uid="sam", email="sam@prepza.dev", email_verified=True
    )

    assert client.post("/superadmin/legal-notices/terms").status_code == 204
    assert client.post("/superadmin/legal-notices/privacy").json()["detail"] == TOO_LATE
    assert client.get("/superadmin/legal-notices").json()[0] == {
        "document": "terms",
        "version": LATER,
        "state": "sending",
        "audience": "everyone",
    }

    app.dependency_overrides.clear()


def test_no_notice_lines_up_with_a_day_past(notices):
    assert legal_notices.earliest_version(date(2026, 10, 14)) == "2026-10-28"
