import asyncio
import base64
import json
from unittest import mock

import pytest
from prepza_common import http, pubsub
from prepza_common.pubsub import PushBody, event_of, publish


class FakeClient:
    def __init__(self):
        self.calls = []

    async def post(self, url, json, headers, timeout):
        self.calls.append((url, json, headers))

        return mock.Mock(raise_for_status=lambda: None)


@pytest.fixture
def client(monkeypatch):
    fake = FakeClient()
    monkeypatch.setattr(http, "get_client", lambda: fake)

    return fake


def test_publishing_to_the_emulator_sends_the_event_without_a_token(client, monkeypatch):
    monkeypatch.setenv("PUBSUB_EMULATOR_HOST", "pubsub:8085")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "demo-prepza")

    asyncio.run(publish("candidate.invited", {"email": "bob@example.com"}))

    [(url, body, headers)] = client.calls
    [message] = body["messages"]
    assert url == "http://pubsub:8085/v1/projects/demo-prepza/topics/events:publish"
    assert message["attributes"] == {"type": "candidate.invited"}
    assert json.loads(base64.b64decode(message["data"])) == {"email": "bob@example.com"}
    assert headers == {}


def test_publishing_to_google_carries_the_services_token(client, monkeypatch):
    monkeypatch.delenv("PUBSUB_EMULATOR_HOST", raising=False)
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "prepza-prod")
    monkeypatch.setattr(pubsub, "access_token", lambda: "google-token")

    asyncio.run(publish("answer.recorded", {}))

    [(url, _, headers)] = client.calls
    assert url == "https://pubsub.googleapis.com/v1/projects/prepza-prod/topics/events:publish"
    assert headers == {"Authorization": "Bearer google-token"}


def test_a_push_decodes_to_its_type_data_and_id():
    body = PushBody.model_validate(
        {
            "message": {
                "data": base64.b64encode(b'{"set_id": "s"}').decode(),
                "attributes": {"type": "generation.completed"},
                "messageId": "42",
            },
            "subscription": "projects/p/subscriptions/companies-events",
        }
    )

    assert event_of(body) == ("generation.completed", {"set_id": "s"}, "42")


def test_a_batch_goes_in_one_call_with_each_events_own_id(client, monkeypatch):
    monkeypatch.setenv("PUBSUB_EMULATOR_HOST", "pubsub:8085")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "demo-prepza")

    asyncio.run(
        pubsub.publish_batch([pubsub.message("a.done", {}, "id-1"), pubsub.message("b.done", {})])
    )

    [(_, body, _)] = client.calls
    assert [message["attributes"] for message in body["messages"]] == [
        {"type": "a.done", "event_id": "id-1"},
        {"type": "b.done"},
    ]


def test_a_push_with_an_event_id_is_known_by_it_across_re_sends():
    body = PushBody.model_validate(
        {
            "message": {
                "attributes": {"type": "candidate.invited", "event_id": "row-1"},
                "messageId": "43",
            },
            "subscription": "projects/p/subscriptions/notifications-events",
        }
    )

    assert event_of(body) == ("candidate.invited", {}, "row-1")
