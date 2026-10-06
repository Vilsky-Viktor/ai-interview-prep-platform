import logging

import httpx
from fastapi import APIRouter
from prepza_common.auth import OptionalUser
from prepza_common.maintenance import is_on, set_on
from prepza_common.superadmin import SuperadminUser, is_superadmin

from app.integrations import rounds
from app.integrations.redis import get_redis
from app.schemas.monitoring import MaintenanceIn, MaintenanceOut, MaintenanceSwitchOut

# Maintenance mode (prepza_common.maintenance): every service reads the switch; it's turned here.
router = APIRouter(tags=["maintenance"])
logger = logging.getLogger(__name__)


@router.get("/maintenance")
async def get_maintenance(user: OptionalUser) -> MaintenanceOut:
    """Public: every page shows the maintenance screen while it's on, except to superadmins."""
    on = await is_on(get_redis())

    return MaintenanceOut(on=on, superadmin=on and user is not None and is_superadmin(user))


async def running() -> int | None:
    """The switch must work even while rounds is down."""
    try:
        return await rounds.running_interviews()
    except httpx.HTTPError:
        logger.warning("Couldn't count the running interviews", exc_info=True)

        return None


@router.get("/superadmin/maintenance")
async def get_switch(superadmin: SuperadminUser) -> MaintenanceSwitchOut:
    return MaintenanceSwitchOut(on=await is_on(get_redis()), running=await running())


@router.put("/superadmin/maintenance")
async def switch(body: MaintenanceIn, superadmin: SuperadminUser) -> MaintenanceSwitchOut:
    """Who switched it and when goes to the logs."""
    await set_on(get_redis(), body.on, superadmin.uid)

    return MaintenanceSwitchOut(on=body.on, running=await running())
