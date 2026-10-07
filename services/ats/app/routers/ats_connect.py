import secrets
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser

from app.config.settings import settings
from app.constants.ats import WEBHOOKS, AtsProvider
from app.helpers.ats import workable_subdomain
from app.integrations import greenhouse, teamtailor, workable
from app.integrations.errors import KeyRejected
from app.schemas.ats import GreenhouseIn, TeamtailorIn, WebhookKeyIn, WebhookOut, WorkableIn
from app.services import ats as integrations
from app.services.access import require_editor
from app.storage import ats

# Connecting each ATS, and the web hooks companies set up themselves (Greenhouse, Teamtailor).
router = APIRouter(tags=["ats"])


async def kept_secret(company_id: UUID, provider: AtsProvider) -> str | None:
    """The web hook secret key of the connection a reconnect replaces, so its web hook goes on
    working."""
    earlier = await ats.connection(company_id, provider)

    return (await integrations.credentials(earlier)).get("webhook_secret") if earlier else None


@router.put("/workable", status_code=status.HTTP_204_NO_CONTENT)
async def connect_workable(company_id: UUID, body: WorkableIn, user: CurrentUser) -> None:
    """Connects Workable with an account's API access token, checked with one read first. A
    second connect replaces the key."""
    await require_editor(user, company_id)
    integrations.require_available()
    subdomain = workable_subdomain(body.account)

    if subdomain is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Enter your Workable address, like acme.workable.com"
        )

    token = body.token.strip()

    try:
        await workable.check(subdomain, token)
    except workable.KeyRejected:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Workable didn't accept this token for that account"
        ) from None

    credentials = integrations.seal({"subdomain": subdomain, "token": token})
    # Who results are written back as: the connecting user's Workable member, or an admin.
    member = await workable.member_id(subdomain, token, user.email)
    await ats.connect(company_id, AtsProvider.WORKABLE, subdomain, credentials, user.uid, member)


@router.put("/greenhouse", status_code=status.HTTP_204_NO_CONTENT)
async def connect_greenhouse(company_id: UUID, body: GreenhouseIn, user: CurrentUser) -> None:
    """Connects Greenhouse with a Harvest V3 (OAuth) API credential, checked with one read
    first. Each connection gets its own secret key for the web hook the company sets up; a
    reconnect keeps it, so the web hook goes on working."""
    await require_editor(user, company_id)
    integrations.require_available()
    client_id, client_secret = body.client_id.strip(), body.client_secret.strip()

    try:
        await greenhouse.check(client_id, client_secret)
    except KeyRejected:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Greenhouse didn't accept this client ID and secret"
        ) from None

    kept = await kept_secret(company_id, AtsProvider.GREENHOUSE)
    sealed = integrations.seal(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "webhook_secret": kept or secrets.token_urlsafe(32),
        }
    )
    # Shown as the credential's last characters: Greenhouse names no account.
    await ats.connect(company_id, AtsProvider.GREENHOUSE, f"…{client_id[-4:]}", sealed, user.uid)


@router.put("/teamtailor", status_code=status.HTTP_204_NO_CONTENT)
async def connect_teamtailor(company_id: UUID, body: TeamtailorIn, user: CurrentUser) -> None:
    """Connects Teamtailor with an Admin, Read/Write API key, checked first in each region until
    one accepts it. The web hook's signature key comes later (Teamtailor makes it); a reconnect
    keeps it."""
    await require_editor(user, company_id)
    integrations.require_available()
    key = body.key.strip()

    try:
        host, company = await teamtailor.region(key)
        await teamtailor.check(host, key)
    except KeyRejected:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Teamtailor didn't accept this key: it needs Admin and Read/Write",
        ) from None

    credentials = {"host": host, "key": key}
    kept = await kept_secret(company_id, AtsProvider.TEAMTAILOR)

    if kept:
        credentials["webhook_secret"] = kept

    # Who results are written back as: the connecting user's Teamtailor user, or an admin.
    member = await teamtailor.member_id(host, key, user.email)
    sealed = integrations.seal(credentials)
    await ats.connect(company_id, AtsProvider.TEAMTAILOR, company, sealed, user.uid, member)


@router.get("/{provider}/webhook")
async def webhook(company_id: UUID, provider: AtsProvider, user: CurrentUser) -> WebhookOut:
    """Where the company's web hook sends its events, and its secret key (empty while a
    Teamtailor one has none saved); owners and admins only."""
    await require_editor(user, company_id)

    if provider not in WEBHOOKS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No web hook to set up")

    connection = await integrations.connected(company_id, provider)
    found = await integrations.credentials(connection)
    url = WEBHOOKS[provider].format(site=settings.site_url, connection_id=connection.id)

    return WebhookOut(url=url, secret=found.get("webhook_secret", ""))


@router.put("/teamtailor/webhook", status_code=status.HTTP_204_NO_CONTENT)
async def save_teamtailor_key(company_id: UUID, body: WebhookKeyIn, user: CurrentUser) -> None:
    """Saves the signature key Teamtailor generated for the company's web hook: its events count
    from then on."""
    await require_editor(user, company_id)
    connection = await integrations.connected(company_id, AtsProvider.TEAMTAILOR)
    found = await integrations.credentials(connection)
    sealed = integrations.seal({**found, "webhook_secret": body.secret.strip()})
    await ats.set_credentials(connection.id, sealed)
