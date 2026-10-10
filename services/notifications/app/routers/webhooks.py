import logging
import time

from fastapi import APIRouter, HTTPException, Request, status
from prepza_common.constants import WEBHOOK_SIGNATURE_REFUSED

from app.config.settings import settings
from app.constants.webhooks import WEBHOOK_TOLERANCE_SECONDS
from app.helpers.webhooks import signature_valid
from app.services.webhooks import handle

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/resend", status_code=status.HTTP_204_NO_CONTENT)
async def resend_webhook(request: Request) -> None:
    """Resend retries until it gets a 2xx, and marking an invite is idempotent, so a failed
    call to its owner simply comes back later."""
    body = await request.body()

    if not signature_valid(
        request.headers.get("svix-id", ""),
        request.headers.get("svix-timestamp", ""),
        request.headers.get("svix-signature", ""),
        body,
        settings.resend_webhook_secret,
        time.time(),
        WEBHOOK_TOLERANCE_SECONDS,
    ):
        logger.error("%s: resend", WEBHOOK_SIGNATURE_REFUSED)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid signature")

    await handle(await request.json())
