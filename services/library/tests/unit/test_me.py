from types import SimpleNamespace

from firebase_admin import auth as firebase_auth

from app.services import accounts

AUTH = {"Authorization": "Bearer good-token"}

CLAIMS = {
    "uid": "user-1",
    "email": "ann@example.com",
    "email_verified": True,
    "name": "Ann",
}


def fake_verify(token):
    if token != "good-token":
        raise firebase_auth.InvalidIdTokenError("bad token")

    return CLAIMS


def test_me_returns_user_from_token(client, monkeypatch):
    monkeypatch.setattr(firebase_auth, "verify_id_token", fake_verify)

    response = client.get("/me", headers={"Authorization": "Bearer good-token"})

    assert response.status_code == 200
    assert response.json() == {**CLAIMS, "language": "en", "is_superadmin": False}


def test_me_says_whether_the_user_is_an_admin(client, monkeypatch):
    monkeypatch.setattr(firebase_auth, "verify_id_token", fake_verify)
    monkeypatch.setenv("SUPERADMIN_EMAILS", "ann@example.com")

    assert client.get("/me", headers=AUTH).json()["is_superadmin"] is True


def test_me_reads_the_language_from_the_token(client, monkeypatch):
    monkeypatch.setattr(
        firebase_auth, "verify_id_token", lambda token: {**CLAIMS, "language": "ru"}
    )

    assert client.get("/me", headers=AUTH).json()["language"] == "ru"


def settings_with(monkeypatch, claims):
    """Stores the language as a sign-in with these claims; returns what was stored and tracked."""
    stored, tracked = {}, []

    async def track(event, **values):
        tracked.append((event, values))

    monkeypatch.setattr(firebase_auth, "verify_id_token", fake_verify)
    monkeypatch.setattr(
        firebase_auth, "get_user", lambda uid: SimpleNamespace(custom_claims=claims)
    )
    monkeypatch.setattr(
        firebase_auth, "set_custom_user_claims", lambda uid, claims: stored.update({uid: claims})
    )
    monkeypatch.setattr(accounts, "track", track)

    return stored, tracked


def test_settings_store_the_language_on_the_sign_in(client, monkeypatch):
    stored, tracked = settings_with(monkeypatch, {"language": "en"})

    response = client.put("/me/settings", json={"language": "ru"}, headers=AUTH)

    assert response.status_code == 204
    assert stored == {"user-1": {"language": "ru"}}
    assert tracked == []


def test_a_new_accounts_first_language_counts_as_signing_up(client, monkeypatch):
    _, tracked = settings_with(monkeypatch, None)

    client.put("/me/settings", json={"language": "de"}, headers=AUTH)

    assert tracked == [("signed_up", {"user_id": "user-1", "language": "de"})]


def test_settings_refuse_an_unknown_language(client, monkeypatch):
    monkeypatch.setattr(firebase_auth, "verify_id_token", fake_verify)

    response = client.put("/me/settings", json={"language": "xx"}, headers=AUTH)

    assert response.status_code == 422


def test_me_rejects_invalid_token(client, monkeypatch):
    monkeypatch.setattr(firebase_auth, "verify_id_token", fake_verify)

    response = client.get("/me", headers={"Authorization": "Bearer bad-token"})

    assert response.status_code == 401


def test_me_requires_token(client):
    response = client.get("/me")

    assert response.status_code == 401
