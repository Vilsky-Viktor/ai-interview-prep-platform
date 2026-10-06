from fastapi import APIRouter
from prepza_common.stats import Month, StatsOut
from prepza_common.superadmin import SuperadminUser

from app.constants.products import CURRENCY
from app.storage import stats

# The superadmin's stats; everyone else gets "not found".
router = APIRouter(prefix="/superadmin", tags=["superadmin"])


@router.get("/stats")
async def get_stats(superadmin: SuperadminUser, month: Month = None) -> StatsOut:
    """Top-ups, what they paid and the credits spent, all time or in one month, for the stats
    tab."""

    return StatsOut(counts=await stats.stats(month), currency=CURRENCY)
