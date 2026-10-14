import asyncio
import uuid

from app.storage import webhooks


def test_a_web_hook_stops_once_however_many_events_find_it_and_starts_again(run):
    async def scenario():
        company = uuid.uuid4()
        hook = await webhooks.add(company, "https://a.example/x", "sealed", "u1", 10)
        stopped = await asyncio.gather(*[webhooks.set_stopped(hook.id, True) for _ in range(2)])
        again = await webhooks.set_stopped(hook.id, True)
        started = await webhooks.set_stopped(hook.id, False)
        await webhooks.remove_company(company)

        return sorted(stopped), again, started

    assert run(scenario()) == ([False, True], False, True)
