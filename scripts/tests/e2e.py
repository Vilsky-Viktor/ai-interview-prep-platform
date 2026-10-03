"""End-to-end test against the running local stack, with real generations (needs OPENAI_API_KEY
in .env; one kit and one interview of a single topic each, a few cents and a few minutes).

A learner signs up, generates a prep kit and practises a round; a company generates an interview
and invites a candidate, who opens the invite and takes it; the company then sees the scorecard
and pays for that candidate. Users come from the Firebase Auth emulator. The candidate uses
Resend's test address, which both Resend and mailpit accept; their invite link is read from the
companies database, since Resend's test inbox can't be read.

Usage: python3 scripts/tests/e2e.py   (standard library only)
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

API = os.getenv("E2E_API", "http://localhost:8090/api")
AUTH = os.getenv("E2E_AUTH", "http://localhost:9199")
POSTGRES = os.getenv("E2E_POSTGRES", "prepza-postgres-1")
KIT_TEXT = "Junior Python developer: Python basics, functions and lists."
INTERVIEW_TEXT = "Backend developer: SQL basics, joins and indexes."
GENERATION_TIMEOUT = 15 * 60


def env(name: str) -> str:
    """From the environment, or else from the repo's .env."""
    if os.getenv(name):
        return os.environ[name]

    for line in (Path(__file__).resolve().parents[2] / ".env").read_text().splitlines():
        if line.startswith(f"{name}="):
            return line.split("=", 1)[1].strip()

    sys.exit(f"{name} isn't set")


def call(method: str, url: str, token: str | None = None, body=None, headers=None):
    request = urllib.request.Request(
        url, data=json.dumps(body).encode() if body is not None else None, method=method
    )
    request.add_header("Content-Type", "application/json")

    for key, value in {
        **(headers or {}),
        **({"Authorization": f"Bearer {token}"} if token else {}),
    }.items():
        request.add_header(key, value)

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()

            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as error:
        sys.exit(f"FAIL {method} {url} -> {error.code} {error.read().decode()[:300]}")


def api(method: str, path: str, token: str, body=None):
    return call(method, API + path, token, body)


def step(message: str) -> None:
    print(f"- {message}", flush=True)


def check(condition: bool, message: str) -> None:
    if not condition:
        sys.exit(f"FAIL {message}")


def wait(what: str, probe, timeout: float = GENERATION_TIMEOUT, every: float = 5):
    """Polls `probe` until it returns something truthy."""
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        found = probe()

        if found:
            return found

        time.sleep(every)

    sys.exit(f"FAIL timed out waiting for {what}")


def sign_up(name: str, verified: bool = False) -> tuple[str, str]:
    """A new emulator user; verified ones get a fresh token carrying email_verified."""
    # Resend's test address takes any +label and is delivered to nobody.
    email = f"delivered+e2e-{name}-{uuid.uuid4().hex[:8]}@resend.dev"
    password = "secret123"
    auth = f"{AUTH}/identitytoolkit.googleapis.com/v1"
    user = call(
        "POST",
        f"{auth}/accounts:signUp?key=demo",
        body={"email": email, "password": password, "returnSecureToken": True},
    )

    if verified:
        project = env("FIREBASE_PROJECT_ID")
        call(
            "POST",
            f"{auth}/projects/{project}/accounts:update",
            body={"localId": user["localId"], "emailVerified": True},
            headers={"Authorization": "Bearer owner"},
        )
        user = call(
            "POST",
            f"{auth}/accounts:signInWithPassword?key=demo",
            body={"email": email, "password": password, "returnSecureToken": True},
        )

    return email, user["idToken"]


def invite_token(invite_id: str) -> str:
    """The token in the invite link the candidate is emailed."""
    query = f"SELECT token FROM candidate_invites WHERE id = '{invite_id}'"
    result = subprocess.run(
        ["docker", "exec", POSTGRES, "psql", "-U", "prepza", "-d", "companies", "-tAc", query],
        capture_output=True,
        text=True,
        check=True,
    )
    token = result.stdout.strip()
    check(bool(token), "the invite has a link")

    return token


def answer_all(kind: str, item_id: str, token: str) -> int:
    """Answers every question with its first option; how many were answered."""
    answered = 0

    while question := api("GET", f"/rounds/{kind}/{item_id}/next", token):
        api(
            "POST",
            f"/rounds/{kind}/{item_id}/answers",
            token,
            {"question_id": question["question_id"], "option_index": 0},
        )
        answered += 1

    return answered


def learner() -> None:
    _, token = sign_up("learner")
    check(
        api("GET", "/billing/me", token)["available"] == 500,
        "a new learner starts with 500 credits",
    )
    step("learner signed up with 500 credits")

    generation = api(
        "POST", "/generate/generations", token, {"text": KIT_TEXT, "kind": "preparation"}
    )
    path = f"/generate/generations/{generation['id']}"
    review = wait(
        "the kit's topics",
        lambda: (row := api("GET", path, token))["status"] == "awaiting_review" and row,
    )
    check(api("GET", "/billing/me", token)["reserved"] == 500, "the kit's credits are set aside")
    api("POST", f"{path}/review", token, {"selected": [0]})
    step(f"topics proposed ({len(review['topics'])}); generating the first")

    done = wait(
        "the kit", lambda: (row := api("GET", path, token))["status"] in ("done", "failed") and row
    )
    check(done["status"] == "done", f"the kit was generated ({done.get('error')})")
    balance = wait(
        "the charge",
        lambda: (row := api("GET", "/billing/me", token))["reserved"] == 0 and row,
        30,
        2,
    )
    check(balance["available"] == 0, "the ready kit is charged")
    step("kit ready and charged")

    preparation = api("GET", f"/library/preparations/{done['preparation_id']}", token)
    round_ = api("POST", "/rounds/rounds", token, {"topic_id": preparation["topics"][0]["id"]})
    answered = answer_all("rounds", round_["id"], token)
    finished = api("POST", f"/rounds/rounds/{round_['id']}/finish", token)
    check(
        finished["status"] == "finished" and finished["final_score"] is not None,
        "the round finishes with a score",
    )
    step(f"round finished: {answered} answers, score {finished['final_score']}%")


def company() -> None:
    _, owner = sign_up("owner")
    company_id = api("POST", "/companies/companies", owner, {"name": "E2E Inc"})["id"]
    credits = f"/companies/companies/{company_id}/credits"
    check(
        api("GET", credits, owner)["available"] == 1_500,
        "a first company starts with 1,500 credits",
    )
    step("company created with 1,500 credits")

    interview = api(
        "POST", f"/companies/interviews?company_id={company_id}", owner, {"text": INTERVIEW_TEXT}
    )
    path = f"/companies/interviews/{interview['id']}"
    wait(
        "the interview's topics",
        lambda: api("GET", f"{path}/generation", owner).get("status") == "awaiting_review",
    )
    api("POST", f"{path}/generation/review", owner, {"selected": [0]})
    wait("the interview", lambda: api("GET", path, owner).get("set_id"))
    step("interview generated")

    email, candidate = sign_up("candidate", verified=True)
    invite = api("POST", f"{path}/candidates", owner, {"email": email})
    check(api("GET", credits, owner)["available"] == 1_200, "the candidate's credits are set aside")
    step("candidate invited; 300 credits set aside")

    token = invite_token(invite["id"])
    sessions = api("POST", f"/companies/invites/{token}/start", candidate)["sessions"]
    answered = 0

    for session in sessions:
        answered += answer_all("sessions", session["id"], candidate)
        api("POST", f"/rounds/sessions/{session['id']}/finish", candidate)

    step(f"candidate took the interview from the invite link: {answered} answers")

    scorecard = wait(
        "the scorecard",
        lambda: (
            (row := api("GET", f"{path}/candidates/{invite['id']}", owner)).get("status")
            == "finished"
            and row
        ),
        60,
        2,
    )
    check(bool(scorecard), "the company sees the finished scorecard")
    balance = wait(
        "the charge",
        lambda: (
            (row := api("GET", f"/companies/companies/{company_id}/credits", owner))["available"]
            == 1_200
            and row
        ),
        30,
        2,
    )
    check(balance["available"] == 1_200, "the answered candidate is charged")
    step("scorecard ready; candidate charged")


if __name__ == "__main__":
    started = time.monotonic()
    print("learner:")
    learner()
    print("company:")
    company()
    print(f"e2e ok in {time.monotonic() - started:.0f}s")
