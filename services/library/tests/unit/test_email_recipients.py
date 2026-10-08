from types import SimpleNamespace

from firebase_admin import auth as firebase_auth

from app.constants.emails import DEFAULTS
from app.storage import emails
from tests.unit.test_internal import token

HEADERS = {"Authorization": f"Bearer {token()}"}


def account(uid, email, language=None, disabled=False):
    claims = {"language": language} if language else None

    return SimpleNamespace(uid=uid, email=email, custom_claims=claims, disabled=disabled)


def test_recipients_have_their_address_language_and_preferences(client, monkeypatch):
    looked_up = []

    def get_users(identifiers):
        looked_up.append([identifier.uid for identifier in identifiers])

        return SimpleNamespace(
            users=[
                account("ann", "ann@example.com", "de"),
                account("bob", "bob@example.com", "xx"),
                account("off", "off@example.com", disabled=True),
                account("phone", None),
            ]
        )

    async def preferences_of(user_ids):
        return {user_id: {**DEFAULTS, "reminders": user_id != "bob"} for user_id in user_ids}

    monkeypatch.setattr(firebase_auth, "get_users", get_users)
    monkeypatch.setattr(emails, "preferences_of", preferences_of)

    response = client.post(
        "/internal/users/email-recipients",
        json={"user_ids": ["ann", "bob", "off", "phone", "gone"]},
        headers=HEADERS,
    )
    found = response.json()["recipients"]

    assert looked_up == [["ann", "bob", "off", "phone", "gone"]]
    # Gone, disabled or without an email: left out. An unknown language is English.
    assert [(item["user_id"], item["email"], item["language"]) for item in found] == [
        ("ann", "ann@example.com", "de"),
        ("bob", "bob@example.com", "en"),
    ]
    assert found[1]["preferences"]["reminders"] is False


def test_firebase_is_asked_at_most_a_hundred_at_a_time(client, monkeypatch):
    sizes = []

    def get_users(identifiers):
        sizes.append(len(identifiers))

        return SimpleNamespace(users=[])

    async def preferences_of(user_ids):
        return {}

    monkeypatch.setattr(firebase_auth, "get_users", get_users)
    monkeypatch.setattr(emails, "preferences_of", preferences_of)

    client.post(
        "/internal/users/email-recipients",
        json={"user_ids": [f"u{index}" for index in range(250)]},
        headers=HEADERS,
    )

    assert sizes == [100, 100, 50]
