from fastapi import APIRouter

from app.schemas.maintenance import RunningOut
from app.service_auth import ServiceCaller
from app.storage import running

router = APIRouter(prefix="/internal/maintenance", tags=["internal"])


@router.get("/running")
async def running_interviews(caller: ServiceCaller) -> RunningOut:
    """For companies' maintenance switch: the candidates who may lose time if it's turned on."""
    return RunningOut(running=await running.running_interviews())
