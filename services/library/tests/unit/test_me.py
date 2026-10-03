from firebase_admin import auth as firebase_auth

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
    assert response.json() == {**CLAIMS, "language": "en"}


def test_me_reads_the_language_from_the_token(client, monkeypatch):
    monkeypatch.setattr(
        firebase_auth, "verify_id_token", lambda token: {**CLAIMS, "language": "ru"}
    )

    assert client.get("/me", headers=AUTH).json()["language"] == "ru"


def test_settings_store_the_language_on_the_sign_in(client, monkeypatch):
    stored = {}
    monkeypatch.setattr(firebase_auth, "verify_id_token", fake_verify)
    monkeypatch.setattr(
        firebase_auth, "set_custom_user_claims", lambda uid, claims: stored.update({uid: claims})
    )

    response = client.put("/me/settings", json={"language": "ru"}, headers=AUTH)

    assert response.status_code == 204
    assert stored == {"user-1": {"language": "ru"}}


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
