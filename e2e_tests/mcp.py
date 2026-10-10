"""End-to-end test of the MCP server (AI apps such as Claude and ChatGPT) against the running local
stack, through the gateway, as an app would: it registers itself, the user allows it on the
consent page's API, it exchanges the code (PKCE) for tokens and calls tools; then refreshes,
revokes, and a second connection is disconnected by the user. A throwaway Auth emulator user;
its account is deleted at the end (which also deletes its connections and company).

Usage: python3 e2e_tests/mcp.py   (standard library only)
"""

import base64
import hashlib
import json
import os
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

SITE = os.getenv("E2E_SITE", "http://localhost:8090")
AUTH = os.getenv("E2E_AUTH", "http://localhost:9199")
REDIRECT = "http://127.0.0.1:33418/callback"
EXCLUDED = {"delete_account", "delete_company"}


def env(name: str) -> str:
    """From the environment, or else from the repo's .env."""
    if os.getenv(name):
        return os.environ[name]

    for line in (Path(__file__).resolve().parents[1] / ".env").read_text().splitlines():
        if line.startswith(f"{name}="):
            return line.split("=", 1)[1].strip()

    sys.exit(f"{name} isn't set")


class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


OPENER = urllib.request.build_opener(NoRedirects)


def send(method: str, url: str, body: bytes | None = None, headers: dict | None = None):
    """(status, headers, parsed JSON or None); errors are answers too."""
    request = urllib.request.Request(url, data=body, method=method, headers=headers or {})

    try:
        with OPENER.open(request, timeout=60) as response:
            raw, status, found = response.read(), response.status, response.headers
    except urllib.error.HTTPError as error:
        raw, status, found = error.read(), error.code, error.headers

    return status, found, json.loads(raw) if raw else None


def post_json(url: str, body, token: str | None = None):
    headers = {"Content-Type": "application/json"}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return send("POST", url, json.dumps(body).encode(), headers)


def post_form(url: str, fields: dict):
    body = urllib.parse.urlencode(fields).encode()

    return send("POST", url, body, {"Content-Type": "application/x-www-form-urlencoded"})


def step(message: str) -> None:
    print(f"- {message}", flush=True)


def check(condition: bool, message: str) -> None:
    if not condition:
        sys.exit(f"FAIL {message}")


def sign_up() -> tuple[str, str, str]:
    """A new emulator user: (local id, email, ID token)."""
    email = f"e2e-mcp-{uuid.uuid4().hex[:8]}@example.com"
    status, _, user = post_json(
        f"{AUTH}/identitytoolkit.googleapis.com/v1/accounts:signUp?key=demo",
        {"email": email, "password": "secret123", "returnSecureToken": True},
    )
    check(status == 200, f"sign-up -> {status}")

    return user["localId"], email, user["idToken"]


def connect(id_token: str, client_name: str) -> tuple[str, dict]:
    """An app registers, the user allows it and it gets its tokens: (client id, tokens)."""
    status, _, client = post_json(
        f"{SITE}/register",
        {
            "client_name": client_name,
            "redirect_uris": [REDIRECT],
            "token_endpoint_auth_method": "none",
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
        },
    )
    check(status == 201 and client.get("client_secret") is None, f"register -> {status}")
    verifier = secrets.token_urlsafe(48)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
    query = urllib.parse.urlencode(
        {
            "client_id": client["client_id"],
            "redirect_uri": REDIRECT,
            "response_type": "code",
            "code_challenge": challenge.decode().rstrip("="),
            "code_challenge_method": "S256",
            "state": "s1",
            "resource": f"{SITE}/mcp",
        }
    )
    status, headers, _ = send("GET", f"{SITE}/authorize?{query}")
    location = headers.get("Location", "")
    check(
        status == 302 and location.startswith(f"{SITE}/connect?request="), f"authorize -> {status}"
    )
    request_id = location.split("request=", 1)[1]
    auth = {"Authorization": f"Bearer {id_token}"}
    status, _, shown = send("GET", f"{SITE}/api/assistant/connect/{request_id}", headers=auth)
    check(status == 200 and shown["redirect_host"] == "127.0.0.1", f"consent -> {status} {shown}")
    check(shown["client_name"] == client_name and shown["known_client"], f"consent shows {shown}")
    status, _, answer = send(
        "POST", f"{SITE}/api/assistant/connect/{request_id}/approve", headers=auth
    )
    check(status == 200 and answer["redirect_url"].startswith(REDIRECT), f"approve -> {status}")
    returned = urllib.parse.parse_qs(urllib.parse.urlparse(answer["redirect_url"]).query)
    check(returned["state"] == ["s1"], "the state comes back")
    status, _, _ = send("POST", f"{SITE}/api/assistant/connect/{request_id}/approve", headers=auth)
    check(status == 404, f"a second answer to the request -> {status}")
    exchange = {
        "grant_type": "authorization_code",
        "code": returned["code"][0],
        "redirect_uri": REDIRECT,
        "client_id": client["client_id"],
        "code_verifier": verifier,
        "resource": f"{SITE}/mcp",
    }
    status, _, wrong = post_form(f"{SITE}/token", {**exchange, "code_verifier": "x" * 50})
    check(status == 400 and wrong["error"] == "invalid_grant", f"a wrong verifier -> {status}")
    status, _, tokens = post_form(f"{SITE}/token", exchange)
    check(status == 200 and tokens["access_token"].startswith("pzm_"), f"token -> {status}")
    status, _, _ = post_form(f"{SITE}/token", exchange)
    check(status == 400, f"the code a second time -> {status}")

    return client["client_id"], tokens


def rpc(access: str, method: str, params: dict | None = None, number: int = 1):
    """One JSON-RPC call to the MCP endpoint: (status, result or error)."""
    status, _, answer = send(
        "POST",
        f"{SITE}/mcp",
        json.dumps(
            {"jsonrpc": "2.0", "id": number, "method": method, "params": params or {}}
        ).encode(),
        {
            "Authorization": f"Bearer {access}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": "2025-06-18",
        },
    )

    return status, (answer or {}).get("result", answer)


def tool(access: str, name: str, arguments: dict) -> tuple[bool, object]:
    """A tool's (error, data) as the app reads them."""
    status, result = rpc(access, "tools/call", {"name": name, "arguments": arguments})
    check(status == 200, f"tools/call {name} -> {status}")

    return result["isError"], json.loads(result["content"][0]["text"])


def main() -> None:
    project = env("FIREBASE_PROJECT_ID")
    local_id, email, id_token = sign_up()

    try:
        step("the endpoint without a token is a 401 that names its resource metadata")
        status, headers, _ = send(
            "POST", f"{SITE}/mcp", b"{}", {"Content-Type": "application/json"}
        )
        check(status == 401 and "resource_metadata=" in headers.get("WWW-Authenticate", ""), "401")
        status, _, metadata = send("GET", f"{SITE}/.well-known/oauth-protected-resource/mcp")
        check(status == 200 and metadata["authorization_servers"] == [SITE], f"resource {metadata}")
        status, _, server = send("GET", f"{SITE}/.well-known/oauth-authorization-server")
        check(status == 200 and server["issuer"] == SITE, f"authorization server {server}")

        step("an app registers, the user allows it, and it gets tokens with PKCE")
        client_id, tokens = connect(id_token, "E2E app")
        access = tokens["access_token"]

        step("initialize, tools/list (the account's and a company's deletion aren't there)")
        status, started = rpc(
            access,
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "e2e", "version": "1"},
            },
        )
        check(status == 200 and started["serverInfo"]["name"] == "prepza", f"initialize {started}")
        status, listed = rpc(access, "tools/list")
        names = {item["name"] for item in listed["tools"]}
        check(status == 200 and "get_me" in names and not names & EXCLUDED, f"{len(names)} tools")
        create = next(item for item in listed["tools"] if item["name"] == "create_company")
        check(create["annotations"]["readOnlyHint"] is False, "create_company is a write")
        print(f"  {len(names)} tools")

        step("tools as the user: get_me, then create_company and list_companies")
        error, me = tool(access, "get_me", {})
        check(not error and me["data"]["email"] == email, f"get_me {me}")
        name = f"MCP e2e {uuid.uuid4().hex[:6]}"
        error, made = tool(access, "create_company", {"name": name})
        check(not error and made["data"]["name"] == name, f"create_company {made}")
        check(all(link.startswith(SITE) for link in made.get("links", [])), "links are absolute")
        error, companies = tool(access, "list_companies", {})
        check(any(item["name"] == name for item in companies["data"]), "the new company is listed")
        error, _ = tool(access, "delete_company", {"company_id": made["data"]["id"]})
        check(error, "delete_company is refused")

        step("the connection is listed for the user")
        auth = {"Authorization": f"Bearer {id_token}"}
        status, _, connections = send("GET", f"{SITE}/api/assistant/connections", headers=auth)
        check(
            status == 200 and [item["client_name"] for item in connections] == ["E2E app"], "listed"
        )

        step("refresh: new tokens; the old refresh token and access stop working")
        refresh = {
            "grant_type": "refresh_token",
            "refresh_token": tokens["refresh_token"],
            "client_id": client_id,
        }
        status, _, renewed = post_form(f"{SITE}/token", refresh)
        check(status == 200 and renewed["access_token"] != access, f"refresh -> {status}")
        status, _, _ = post_form(f"{SITE}/token", refresh)
        check(status == 400, f"the old refresh token -> {status}")
        check(rpc(access, "tools/list")[0] == 401, "the old access token is refused")
        access = renewed["access_token"]
        check(rpc(access, "tools/list")[0] == 200, "the new access token works")

        step("the app revokes its token: the connection is gone")
        status, _, _ = post_form(f"{SITE}/revoke", {"token": access, "client_id": client_id})
        check(status == 200 and rpc(access, "tools/list")[0] == 401, "revoked")

        step("a second app; the user disconnects it")
        _, second = connect(id_token, "Second app")
        status, _, connections = send("GET", f"{SITE}/api/assistant/connections", headers=auth)
        check([item["client_name"] for item in connections] == ["Second app"], "one connection")
        url = f"{SITE}/api/assistant/connections/{connections[0]['id']}"
        status, _, _ = send("DELETE", url, headers=auth)
        check(status == 204 and rpc(second["access_token"], "tools/list")[0] == 401, "disconnected")
    finally:
        # The account goes the way a user deletes it (with its company and connections).
        send("DELETE", f"{SITE}/api/library/me", headers={"Authorization": f"Bearer {id_token}"})
        send(
            "POST",
            f"{AUTH}/identitytoolkit.googleapis.com/v1/projects/{project}/accounts:delete",
            json.dumps({"localId": local_id}).encode(),
            {"Authorization": "Bearer owner", "Content-Type": "application/json"},
        )
        print("clean-up: the throwaway account is deleted")

    print("mcp ok")


if __name__ == "__main__":
    main()
