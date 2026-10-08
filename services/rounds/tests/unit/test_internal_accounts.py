from prepza_common.service_auth import issue_token

from app.storage import accounts

HEADERS = {
    "Authorization": "Bearer "
    + issue_token("library", "rounds", "test-secret-that-is-at-least-32-bytes")
}


def test_library_exports_a_users_sessions_with_a_post(client, monkeypatch):
    async def export(user_id):
        return {"interview_sections": [user_id]}

    monkeypatch.setattr(accounts, "export", export)

    response = client.post("/internal/users/ann/export", headers=HEADERS)

    assert response.json() == {"interview_sections": ["ann"]}
