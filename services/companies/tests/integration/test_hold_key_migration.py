from prepza_common.credit_keys import invite_key, ledger_key
from sqlalchemy import text

from app.storage.db import Session

INTERVIEW = "1b4e28ba-2fa1-11d2-883f-0016d3cca427"


def test_companies_and_billing_rewrite_old_keys_to_the_same_new_key_without_the_email(run):
    """Each service rewrites its own copy of a candidate's key; they must still meet."""

    async def scenario():
        rows = [
            # An invite's own key, and an older invite's "{interview_id}:{email}".
            (f"{INTERVIEW}:carol@example.com:0f1e2d3c4b5a69788796a5b4c3d2e1f0", None),
            (None, "Ben@Example.com"),
        ]
        found = []

        async with Session() as session:
            for stored, email in rows:
                old_key = "coalesce(hold_key, interview_id::text || ':' || lower(email))"
                companies = await session.scalar(
                    text(
                        f"SELECT {invite_key('interview_id', old_key)} FROM (SELECT CAST(:interview AS uuid) AS "
                        "interview_id, CAST(:stored AS text) AS hold_key, CAST(:email AS text) "
                        "AS email) AS invite"
                    ),
                    {"interview": INTERVIEW, "stored": stored, "email": email},
                )
                old = stored or f"{INTERVIEW}:{email.lower()}"
                billing = await session.scalar(
                    text(
                        f"SELECT {ledger_key('key')} FROM (SELECT CAST(:key AS text) AS key) AS hold"
                    ),
                    {"key": f"candidate:{old}"},
                )
                found.append((companies, billing))

        return found

    for companies, billing in run(scenario()):
        assert billing == f"candidate:{companies}"
        assert companies.startswith(f"{INTERVIEW}:")
        assert "@" not in companies
