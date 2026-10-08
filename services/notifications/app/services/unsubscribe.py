from app.constants.unsubscribe import USER_SETTINGS, UnsubscribeType
from app.integrations import library
from app.storage import opt_outs


async def apply(payload: dict) -> None:
    """Applies a checked unsubscribe token: a user's email settings (library keeps them), or a
    candidate's wish to hear no more from a company, or about one invite's reminders."""
    kind = UnsubscribeType(payload["type"])

    if kind in USER_SETTINGS:
        await library.unsubscribe(payload["user_id"], USER_SETTINGS[kind])

        return

    invite_id = payload["invite_id"] if kind == UnsubscribeType.INVITE_REMINDERS else None
    await opt_outs.add(payload["address"], payload["company_id"], invite_id)
