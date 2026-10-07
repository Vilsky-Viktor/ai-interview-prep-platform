from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder

from app.service_auth import ServiceCaller
from app.storage import ats_candidates

router = APIRouter(prefix="/internal", tags=["internal"])


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, email: str, caller: ServiceCaller) -> None:
    """Library, deleting an account: an ATS's records of them as a candidate go."""
    await ats_candidates.delete_email(email)


@router.get("/users/{user_id}/export")
async def export_user(user_id: str, email: str, caller: ServiceCaller) -> dict:
    """Library, for "Download my data": what ATSs sent about them as a candidate."""
    return jsonable_encoder(
        {
            "ats_candidates": [
                {
                    "email": row.email,
                    "interview_id": row.interview_id,
                    "status": row.status,
                    "results_sent_at": row.reported_at,
                    "at": row.created_at,
                }
                for row in await ats_candidates.of_email(email)
            ],
        }
    )
