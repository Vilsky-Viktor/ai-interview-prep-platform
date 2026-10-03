from prepza_common.translations import TRANSLATIONS

from app.constants.generation import GENERATIONS_PAUSED


def test_messages_users_see_have_translations():
    for language in TRANSLATIONS.values():
        assert GENERATIONS_PAUSED in language
