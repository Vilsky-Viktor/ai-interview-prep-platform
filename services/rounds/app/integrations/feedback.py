from uuid import UUID

import httpx

from app.config.settings import settings
from app.service_auth import service_token


async def _request(method: str, path: str, **kwargs) -> httpx.Response:
    async with httpx.AsyncClient(timeout=30) as client:
        return await client.request(
            method,
            f"{settings.library_url}/internal/questions{path}",
            headers={"Authorization": f"Bearer {service_token()}"},
            **kwargs,
        )


async def get_rating(question_id: UUID, user_id: str) -> httpx.Response:
    return await _request("GET", f"/{question_id}/rating", params={"user_id": user_id})


async def rate(question_id: UUID, user_id: str, value: int) -> httpx.Response:
    return await _request(
        "PUT", f"/{question_id}/rating", json={"user_id": user_id, "value": value}
    )


async def my_report(question_id: UUID, user_id: str) -> httpx.Response:
    return await _request("GET", f"/{question_id}/reports/mine", params={"user_id": user_id})


async def report(question_id: UUID, user_id: str, reason: str, comment: str) -> httpx.Response:
    return await _request(
        "POST",
        f"/{question_id}/reports",
        json={"user_id": user_id, "reason": reason, "comment": comment},
    )
