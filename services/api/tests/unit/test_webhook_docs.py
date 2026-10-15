import json
from datetime import UTC, datetime

import pytest

from app.helpers.webhooks import body_of
from app.main import app


@pytest.mark.parametrize(
    "event",
    [
        "candidate.finished",
        "candidate.started",
        "candidate.undelivered",
        "candidate.expired",
        "candidate.removed",
        "interview.ready",
        "test",
    ],
)
def test_the_reference_shows_each_events_body_as_its_sent(event):
    spec = app.openapi()
    body = spec["webhooks"][event]["post"]["requestBody"]["content"]["application/json"]
    name = body["schema"]["$ref"].rsplit("/", 1)[-1]
    sent = json.loads(body_of("evt_1", event, {}, datetime.now(UTC)))

    assert set(spec["components"]["schemas"][name]["properties"]) == set(sent)
