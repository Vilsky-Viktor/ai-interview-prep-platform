import asyncio

from firebase_admin import auth as firebase_auth
from prepza_common.auth import claims_language

from app.constants.emails import FIREBASE_LOOKUP_LIMIT
from app.storage import emails


async def recipients(user_ids: list[str]) -> list[dict]:
    """Each user's sign-in email, interface language and email preferences; users who are gone,
    disabled or have no email are left out."""
    accounts = []

    for start in range(0, len(user_ids), FIREBASE_LOOKUP_LIMIT):
        chunk = user_ids[start : start + FIREBASE_LOOKUP_LIMIT]
        found = await asyncio.to_thread(
            firebase_auth.get_users, [firebase_auth.UidIdentifier(uid) for uid in chunk]
        )
        accounts += [account for account in found.users if account.email and not account.disabled]

    preferences = await emails.preferences_of([account.uid for account in accounts])

    return [
        {
            "user_id": account.uid,
            "email": account.email,
            "language": claims_language(account.custom_claims or {}),
            "preferences": preferences[account.uid],
        }
        for account in accounts
    ]
