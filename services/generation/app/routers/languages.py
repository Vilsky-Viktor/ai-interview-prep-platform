from fastapi import APIRouter
from prepza_common.constants import LANGUAGES

router = APIRouter(tags=["languages"])


@router.get("/languages")
async def list_languages() -> list[str]:
    """The languages kits and interviews can be generated in, for the "generate in" choice."""
    return list(LANGUAGES)
