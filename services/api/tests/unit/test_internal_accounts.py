from prepza_common.service_auth import issue_token

from app.storage import keys, webhooks

HEADERS = {
    "Authorization": "Bearer "
    + issue_token("library", "api", "test-secret-that-is-at-least-32-bytes")
}


async def nothing(user_id):
    return []


def test_library_deletes_and_exports_a_users_keys_and_web_hooks_by_id_alone(client, monkeypatch):
    removed = []

    async def remove_user(user_id):
        removed.append(user_id)

    monkeypatch.setattr(keys, "remove_user", remove_user)
    monkeypatch.setattr(webhooks, "remove_user", remove_user)
    monkeypatch.setattr(keys, "of_user", nothing)
    monkeypatch.setattr(webhooks, "of_user", nothing)

    deleted = client.request(
        "DELETE", "/internal/users/ann", json={"email": "ann@example.com"}, headers=HEADERS
    )
    exported = client.post(
        "/internal/users/ann/export", json={"email": "ann@example.com"}, headers=HEADERS
    )

    assert deleted.status_code == 204
    assert removed == ["ann", "ann"]
    assert exported.json() == {"api_keys": [], "webhooks": []}
