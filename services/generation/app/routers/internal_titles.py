from fastapi import APIRouter

from app.schemas.titles import TitleCheckIn, TitleCheckOut
from app.service_auth import ServiceCaller
from app.services.titles import check_title

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/titles/check")
async def check(body: TitleCheckIn, caller: ServiceCaller) -> TitleCheckOut:
    """For library, before a kit is public: whether its title names a company."""
    return await check_title(body.title)
