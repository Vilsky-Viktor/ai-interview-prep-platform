from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from prepza_common.constants import RATE_LIMITED
from prepza_common.i18n import add_localized_errors
from pydantic import BaseModel, field_validator


class Body(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def required(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Title is required")

        return value


app = FastAPI()
add_localized_errors(app)


@app.get("/limited")
def limited():
    raise HTTPException(429, RATE_LIMITED)


@app.get("/unknown")
def unknown():
    raise HTTPException(409, "Something only English has")


@app.post("/titles")
def titles(body: Body):
    return body


client = TestClient(app)


def test_errors_come_in_the_interface_language():
    response = client.get("/limited", headers={"Accept-Language": "ru"})

    assert response.status_code == 429
    assert response.json() == {"detail": "Слишком много запросов. Попробуйте позже."}


def test_english_and_unknown_languages_keep_the_message():
    assert client.get("/limited").json() == {"detail": RATE_LIMITED}
    assert client.get("/limited", headers={"Accept-Language": "sv-SE"}).json() == {
        "detail": RATE_LIMITED
    }


def test_a_message_without_a_translation_stays_english():
    response = client.get("/unknown", headers={"Accept-Language": "ru"})

    assert response.json() == {"detail": "Something only English has"}


def test_validator_messages_are_translated_too():
    response = client.post("/titles", json={"title": " "}, headers={"Accept-Language": "ru"})

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, Нужно название"


def test_every_translation_language_is_offered():
    from prepza_common.constants import LANGUAGES
    from prepza_common.translations import TRANSLATIONS

    assert set(TRANSLATIONS) <= set(LANGUAGES)


def test_every_language_translates_every_message():
    from prepza_common.constants import DEFAULT_LANGUAGE, LANGUAGES
    from prepza_common.translations import TRANSLATIONS

    english = set(TRANSLATIONS["ru"])

    assert set(TRANSLATIONS) == set(LANGUAGES) - {DEFAULT_LANGUAGE}
    assert all(set(messages) == english for messages in TRANSLATIONS.values())


def test_a_three_letter_language_with_a_region_is_read_whole():
    response = client.get("/limited", headers={"Accept-Language": "fil-PH,fil;q=0.9"})

    assert response.json() == {"detail": "Masyadong maraming request. Subukang muli mamaya."}
