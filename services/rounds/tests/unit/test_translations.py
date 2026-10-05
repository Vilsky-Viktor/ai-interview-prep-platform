from prepza_common.translations import TRANSLATIONS

from app.constants.rounds import CHAT_FAILED


def test_messages_users_see_have_translations():
    for language in TRANSLATIONS.values():
        assert CHAT_FAILED in language
