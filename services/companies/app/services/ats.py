import json
import logging

from cryptography.fernet import Fernet
from fastapi import HTTPException, status

from app.config.settings import settings
from app.constants.ats import WORKABLE_WEBHOOK
from app.helpers.encryption import decrypt, encrypt
from app.integrations import workable
from app.models.ats import AtsConnection
from app.storage import ats


def available() -> bool:
    """Whether integrations are set up here: a valid encryption key."""
    try:
        Fernet(settings.ats_encryption_key)
    except ValueError:
        return False

    return True


def require_available() -> None:
    if not available():
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Integrations aren't set up")


def seal(credentials: dict) -> str:
    return encrypt(settings.ats_encryption_key, json.dumps(credentials))


async def workable_key(connection: AtsConnection) -> tuple[str, str]:
    """The connection's subdomain and token. A key that can't be read any more (the encryption
    key changed) marks the connection broken, like one Workable refuses."""
    opened = decrypt(settings.ats_encryption_key, connection.credentials)

    if opened is None:
        await broken(connection)

    credentials = json.loads(opened)

    return credentials["subdomain"], credentials["token"]


async def broken(connection: AtsConnection) -> None:
    """Marks the connection for reconnecting, and tells the company."""
    await ats.mark_broken(connection.id)

    raise HTTPException(
        status.HTTP_409_CONFLICT, "Workable no longer accepts the key: reconnect to continue"
    )


async def connected(company_id, provider: str) -> AtsConnection:
    require_available()
    connection = await ats.connection(company_id, provider)

    if connection is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not connected")

    return connection


async def jobs(connection: AtsConnection) -> list[dict]:
    subdomain, token = await workable_key(connection)

    try:
        return await workable.jobs(subdomain, token)
    except workable.KeyRejected:
        await broken(connection)


async def stages(connection: AtsConnection, job_id: str) -> list[dict]:
    subdomain, token = await workable_key(connection)

    try:
        return await workable.stages(subdomain, token, job_id)
    except workable.KeyRejected:
        await broken(connection)


async def job(connection: AtsConnection, job_id: str) -> dict:
    subdomain, token = await workable_key(connection)

    try:
        return await workable.job(subdomain, token, job_id)
    except workable.KeyRejected:
        await broken(connection)


async def subscribe(connection: AtsConnection, link_id, job_id: str, stage_id: str) -> str:
    """Asks Workable to send this link's candidates (moved into the stage) to its own address."""
    subdomain, token = await workable_key(connection)
    target = WORKABLE_WEBHOOK.format(site=settings.site_url, link_id=link_id)

    try:
        return await workable.subscribe(subdomain, token, target, job_id, stage_id)
    except workable.KeyRejected:
        await broken(connection)


async def unsubscribe(connection: AtsConnection, subscription_ids: list[str]) -> None:
    """Cancels Workable's notifications, as far as Workable answers: a link or connection goes
    either way, and events for it are ignored after."""
    for subscription_id in subscription_ids:
        try:
            subdomain, token = await workable_key(connection)
            await workable.unsubscribe(subdomain, token, subscription_id)
        except (HTTPException, workable.KeyRejected):
            logging.getLogger(__name__).warning(
                "Couldn't cancel Workable subscription %s", subscription_id
            )
