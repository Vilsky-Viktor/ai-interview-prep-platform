from starlette.applications import Starlette
from starlette.responses import RedirectResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from app.constants.mcp import CONNECT_COOKIE, CONNECT_COOKIE_PATH
from app.helpers.authorize_guard import GuardAuthorize, request_of


def redirecting(location: str) -> TestClient:
    async def authorize(scope, receive, send):
        await RedirectResponse(location, status_code=302)(scope, receive, send)

    app = Starlette(routes=[Route("/authorize", endpoint=GuardAuthorize(authorize))])

    return TestClient(app, follow_redirects=False)


def test_sending_the_browser_to_the_consent_page_marks_it_for_that_request():
    response = redirecting("https://prepza.ai/connect?request=r1").get("/authorize")
    marked = response.headers["set-cookie"]

    assert marked.startswith(f"{CONNECT_COOKIE}=r1;")
    assert f"Path={CONNECT_COOKIE_PATH}" in marked
    assert "HttpOnly" in marked and "SameSite=Lax" in marked


def test_an_error_is_a_page_never_a_redirect_to_the_apps_address():
    """Anyone can register an app with any address: redirecting errors there would make
    /authorize an open redirect."""
    response = redirecting("https://evil.example/cb?error=invalid_request").get("/authorize")

    assert response.status_code == 400
    assert "location" not in response.headers and "set-cookie" not in response.headers
    assert "isn't valid" in response.text


def test_only_the_consent_page_carries_a_request():
    assert request_of("https://prepza.ai/connect?request=r1") == "r1"
    assert request_of("https://evil.example/connect-x?request=r1") is None
