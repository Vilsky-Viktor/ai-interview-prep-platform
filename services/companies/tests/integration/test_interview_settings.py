import uuid

from app.schemas.interviews import InterviewSettings
from app.storage import companies, interviews


def test_saving_one_setting_keeps_the_others(run):
    async def scenario():
        company = await companies.create(f"Acme {uuid.uuid4()}", "owner", "owner@example.com")
        found = await interviews.create(company.id, uuid.uuid4(), "en")
        await interviews.update_settings(
            found.id, InterviewSettings(question_seconds=45, pass_mark=85)
        )
        await interviews.update_settings(found.id, InterviewSettings(hired=True))

        return await interviews.get(found.id)

    saved = run(scenario())

    assert (saved.question_seconds, saved.pass_mark, saved.hired) == (45, 85, True)
