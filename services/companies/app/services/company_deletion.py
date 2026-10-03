from app.helpers.interviews import attach_set
from app.integrations import billing, library, rounds
from app.integrations import generation as generation_api
from app.storage import companies, interviews


async def delete_company(company_id) -> None:
    """Each interview's results and questions go first, so a failure leaves the company to
    delete again."""
    for interview in await interviews.list_for_company(company_id):
        if interview.set_id is None:
            cancelled = await generation_api.cancel(interview.generation_id, company_id)

            if cancelled.is_server_error:
                cancelled.raise_for_status()

            interview = await attach_set(interview)

        if interview.set_id:
            await rounds.delete_interview_data(interview.set_id)
            await library.delete_interview(interview.set_id)

    await companies.delete(company_id)
    await billing.delete_company(company_id)
