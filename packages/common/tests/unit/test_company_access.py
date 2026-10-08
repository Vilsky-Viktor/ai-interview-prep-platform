import asyncio

import httpx
import pytest
from fastapi import HTTPException
from prepza_common import company_access, http

URL = "http://companies"


@pytest.fixture
def answering(monkeypatch):
    """Companies answering with `status` and `body`; every request it got is kept."""
    seen = []

    def use(status, body=None):
        def handler(request):
            seen.append(request)

            return httpx.Response(status, json=body)

        monkeypatch.setattr(
            http, "get_client", lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler))
        )

        return seen

    return use


def test_access_asks_companies_for_the_users_role(answering):
    seen = answering(200, {"member": True, "editor": False})

    found = asyncio.run(company_access.access(URL, "token", "c1", "ann"))

    assert found == {"member": True, "editor": False}
    [request] = seen
    assert request.url.path == "/internal/companies/c1/access"
    assert request.url.params["user_id"] == "ann"
    assert request.headers["Authorization"] == "Bearer token"


def test_a_company_thats_gone_is_no_access(answering):
    answering(404, {"detail": "Company not found"})

    found = asyncio.run(company_access.access(URL, "token", "c1", "ann"))

    assert found == {"member": False, "editor": False}


def test_companies_failing_raises(answering):
    answering(503, {"detail": "Busy"})

    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(company_access.access(URL, "token", "c1", "ann"))


@pytest.mark.parametrize(
    ("found", "editor", "status"),
    [
        ({"member": False, "editor": False}, False, 404),
        ({"member": False, "editor": False}, True, 404),
        ({"member": True, "editor": False}, True, 403),
    ],
)
def test_require_refuses_who_may_not(found, editor, status):
    with pytest.raises(HTTPException) as refused:
        company_access.require(found, editor)

    assert refused.value.status_code == status


@pytest.mark.parametrize(
    ("found", "editor"),
    [({"member": True, "editor": False}, False), ({"member": True, "editor": True}, True)],
)
def test_require_lets_members_look_and_editors_change(found, editor):
    company_access.require(found, editor)
