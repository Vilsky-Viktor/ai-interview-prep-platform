from types import SimpleNamespace

import httpx
import pytest
from fastapi import HTTPException
from openai import APIConnectionError
from prepza_common.user import User

from app.auth import user_with_token
from app.constants.transcribe import MAX_AUDIO_BYTES
from app.main import app
from app.services import transcribe

ANN = User(uid="ann", email="ann@example.com", email_verified=True)
WEBM = {"Content-Type": "audio/webm;codecs=opus"}


@pytest.fixture
def openai(monkeypatch):
    """OpenAI's speech to text, answering `answer.text`; the calls it got, and what was counted."""
    calls = []
    recorded = []
    answer = SimpleNamespace(text="Who passed?", usage=SimpleNamespace(total_tokens=42))

    async def create(**arguments):
        calls.append(arguments)

        if isinstance(answer.text, Exception):
            raise answer.text

        return answer

    async def not_paused(redis):
        pass

    async def check_transcription(redis, user_id):
        pass

    async def record(redis, user_id, company_id, tokens):
        recorded.append((user_id, company_id, tokens))

    client = SimpleNamespace(audio=SimpleNamespace(transcriptions=SimpleNamespace(create=create)))
    monkeypatch.setattr(transcribe, "get_openai", lambda: client)
    monkeypatch.setattr(transcribe, "refuse_if_paused", not_paused)
    monkeypatch.setattr(transcribe.limits, "check_transcription", check_transcription)
    monkeypatch.setattr(transcribe.limits, "record", record)
    app.dependency_overrides[user_with_token] = lambda: (ANN, "user-token")

    yield SimpleNamespace(calls=calls, recorded=recorded, answer=answer)

    app.dependency_overrides.clear()


def test_a_recording_is_heard_in_the_interface_language_and_its_tokens_count(client, openai):
    response = client.post(
        "/transcribe", content=b"opus", headers={**WEBM, "Accept-Language": "de"}
    )

    assert response.json() == {"text": "Who passed?"}
    [call] = openai.calls
    assert call["file"] == ("audio.webm", b"opus", "audio/webm")
    assert call["language"] == "de"
    assert call["model"] == "gpt-4o-mini-transcribe"
    assert openai.recorded == [("ann", None, 42)]


def test_filipino_is_heard_as_tagalog(client, openai):
    headers = {"Content-Type": "audio/mp4", "Accept-Language": "fil"}
    client.post("/transcribe", content=b"aac", headers=headers)

    assert openai.calls[0]["language"] == "tl"
    assert openai.calls[0]["file"][0] == "audio.mp4"


def test_another_format_or_a_larger_recording_is_refused_before_openai(client, openai):
    response = client.post("/transcribe", content=b"x", headers={"Content-Type": "audio/wav"})
    assert response.status_code == 415

    large = b"x" * (MAX_AUDIO_BYTES + 1)
    response = client.post("/transcribe", content=large, headers=WEBM)
    assert response.status_code == 413

    response = client.post("/transcribe", content=b"", headers=WEBM)
    assert response.status_code == 422
    assert openai.calls == []


@pytest.mark.parametrize("text", ["", "  "])
def test_nothing_heard_is_a_422_in_the_users_language(client, openai, text):
    openai.answer.text = text
    response = client.post(
        "/transcribe", content=b"opus", headers={**WEBM, "Accept-Language": "de"}
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Es war nichts zu hören. Versuche es erneut."


def test_openai_failing_is_a_502_and_nothing_is_logged_of_the_recording(client, openai, caplog):
    openai.answer.text = APIConnectionError(request=httpx.Request("POST", "https://api.openai.com"))
    response = client.post("/transcribe", content=b"secret-audio", headers=WEBM)

    assert response.status_code == 502
    assert "secret-audio" not in caplog.text


def test_paused_or_over_a_limit_is_refused_before_openai(client, openai, monkeypatch):
    async def over(redis, user_id):
        raise HTTPException(429, "over")

    monkeypatch.setattr(transcribe.limits, "check_transcription", over)
    assert client.post("/transcribe", content=b"opus", headers=WEBM).status_code == 429

    async def paused(redis):
        raise HTTPException(503, "paused")

    monkeypatch.setattr(transcribe, "refuse_if_paused", paused)
    assert client.post("/transcribe", content=b"opus", headers=WEBM).status_code == 503
    assert openai.calls == []


def test_signed_out_is_refused(client):
    assert client.post("/transcribe", content=b"opus", headers=WEBM).status_code in (401, 403)
