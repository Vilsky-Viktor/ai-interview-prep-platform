from prepza_common.constants import LANGUAGES
from prepza_common.translations import TRANSLATIONS

from app.constants.certificate_rules import CERTIFICATE_RULES
from app.constants.rounds import CHAT_FAILED, PUBLIC_TOPICS_LIMIT


def test_messages_users_see_have_translations():
    for language in TRANSLATIONS.values():
        assert CHAT_FAILED in language


def test_certificate_rules_come_in_every_language(client):
    assert set(CERTIFICATE_RULES) == set(LANGUAGES)

    english = client.get("/certificates/rules").json()
    russian = client.get("/certificates/rules", headers={"Accept-Language": "ru"}).json()

    assert english == CERTIFICATE_RULES["en"]
    assert russian == CERTIFICATE_RULES["ru"]


def test_limit_messages_have_translations():
    for language in TRANSLATIONS.values():
        assert PUBLIC_TOPICS_LIMIT in language
