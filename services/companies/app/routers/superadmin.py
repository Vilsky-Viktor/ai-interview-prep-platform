from fastapi import APIRouter
from prepza_common.paging import PageParams
from prepza_common.superadmin import SuperadminUser

from app.constants.monitoring import PassRateSort
from app.helpers.pass_rates import outside_triggers, percent
from app.integrations import rounds
from app.schemas.monitoring import PassRateOut
from app.storage import pass_rates

# The superadmin's monitoring (docs/compliance/post-market-monitoring-plan.md); everyone else
# gets "not found".
router = APIRouter(prefix="/superadmin", tags=["superadmin"])


@router.get("/pass-rates")
async def list_pass_rates(
    superadmin: SuperadminUser, page: PageParams, sort: PassRateSort = PassRateSort.PASS_RATE
) -> list[PassRateOut]:
    rows = await pass_rates.page(sort == PassRateSort.FINISHED, page.offset, page.limit)
    answers = await rounds.answer_counts([row.set_id for row in rows if row.set_id])

    return [
        PassRateOut(
            interview_id=row.id,
            title=row.title,
            company=row.company,
            finished=row.finished,
            pass_rate=percent(row.passed, row.finished),
            pass_mark=row.pass_mark,
            average_grade=round(row.average),
            timeout_share=percent(*answers.get(str(row.set_id), (0, 0))),
            outside_triggers=outside_triggers(row.passed, row.finished),
        )
        for row in rows
    ]
