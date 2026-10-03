from prepza_common.translations import TRANSLATIONS

from app.constants.credits import NOT_ENOUGH


def test_messages_users_see_have_translations():
    for language in TRANSLATIONS.values():
        assert NOT_ENOUGH in language
