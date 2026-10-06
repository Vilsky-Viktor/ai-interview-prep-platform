from app.routers import internal_maintenance
from app.service_auth import service_token


def test_the_running_count_is_for_services_only(client, monkeypatch):
    async def three():
        return 3

    monkeypatch.setattr(internal_maintenance.running, "running_interviews", three)

    assert client.get("/internal/maintenance/running").status_code == 401

    response = client.get(
        "/internal/maintenance/running",
        headers={"Authorization": f"Bearer {service_token('rounds')}"},
    )

    assert response.json() == {"running": 3}
