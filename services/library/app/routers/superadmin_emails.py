import logging

from fastapi import APIRouter, HTTPException, status
from prepza_common.superadmin import SuperadminUser
from prepza_common.user import UserEmailIn

from app.constants.emails import ConsentSource
from app.schemas.emails import (
    AdminEmailChangesIn,
    EmailAccountOut,
    EmailLookupOut,
    EmailPreferencesOut,
)
from app.services.accounts import account_by_email, account_exists
from app.storage import emails

# The admin zone's emails tab: a superadmin stops a user's emails for someone who asked prepza
# directly. Everyone else gets "not found". Addresses go in the body, never the query string,
# which request logs record.
router = APIRouter(prefix="/superadmin/emails", tags=["superadmin"])
logger = logging.getLogger(__name__)


@router.post("/lookup")
async def look_up(body: UserEmailIn, superadmin: SuperadminUser) -> EmailLookupOut:
    """The account signed in with the address, whatever its case, with its email settings."""
    account = await account_by_email(body.email)

    if account is None:
        return EmailLookupOut(account=None)

    return EmailLookupOut(
        account=EmailAccountOut(
            user_id=account.uid,
            email=account.email,
            preferences=EmailPreferencesOut(**await emails.preferences(account.uid)),
        )
    )


@router.put("/{user_id}/preferences")
async def change_preferences(
    user_id: str, body: AdminEmailChangesIn, superadmin: SuperadminUser
) -> EmailPreferencesOut:
    """Changes some of the user's settings, each change logged with the admin source and the
    superadmin's id. Safe to repeat: a setting already as asked logs nothing."""
    if not await account_exists(user_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")

    saved = await emails.change(user_id, body.changes, ConsentSource.ADMIN, superadmin.uid)
    logger.warning(
        "Email settings of user %s changed by superadmin %s: %s",
        user_id,
        superadmin.uid,
        {setting.value: on for setting, on in body.changes.items()},
    )

    return EmailPreferencesOut(**saved)
