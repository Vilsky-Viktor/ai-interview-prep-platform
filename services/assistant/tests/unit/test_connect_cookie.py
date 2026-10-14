from starlette.applications import Starlette
from starlette.responses import RedirectResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from app.constants.mcp import CONNECT_COOKIE, CONNECT_COOKIE_PATH
from app.helpers.connect_cookie import MarkBrowser, request_of


def redirecting(location: str) -> TestClient:
    async def authorize(scope, receive, send):
        await RedirectResponse(location, status_code=302)(scope, receive, send)

    app = Starlette(routes=[Route("/authorize", endpoint=MarkBrowser(authorize))])

    return TestClient(app, follow_redirects=False)


def test_sending_the_browser_to_the_consent_page_marks_it_for_that_request():
    response = redirecting("https://prepza.ai/connect?request=r1").get("/authorize")
    marked = response.headers["set-cookie"]

    assert marked.startswith(f"{CONNECT_COOKIE}=r1;")
    assert f"Path={CONNECT_COOKIE_PATH}" in marked
    assert "HttpOnly" in marked and "SameSite=Lax" in marked


def test_an_error_sent_back_to_the_app_marks_nothing():
    response = redirecting("https://claude.ai/callback?error=invalid_request").get("/authorize")

    assert "set-cookie" not in response.headers


def test_only_the_consent_page_carries_a_request():
    assert request_of("https://prepza.ai/connect?request=r1") == "r1"
    assert request_of("https://evil.example/connect-x?request=r1") is None
