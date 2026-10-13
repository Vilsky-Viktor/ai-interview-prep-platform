from datetime import timedelta

from fastapi import APIRouter, status

from app.schemas.maintenance import ResumeIn, RunningOut
from app.service_auth import ServiceCaller
from app.storage import running

router = APIRouter(prefix="/internal/maintenance", tags=["internal"])


@router.get("/running")
async def running_interviews(caller: ServiceCaller) -> RunningOut:
    """For companies' maintenance switch: the candidates who may lose time if it's turned on."""
    return RunningOut(running=await running.running_interviews())


@router.post("/resume", status_code=status.HTTP_204_NO_CONTENT)
async def resume(body: ResumeIn, caller: ServiceCaller) -> None:
    """For companies' maintenance switch, before it turns off: running interviews get back the
    time it was on."""
    await running.give_time_back(timedelta(seconds=body.seconds))
