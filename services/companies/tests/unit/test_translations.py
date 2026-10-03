from prepza_common.translations import TRANSLATIONS

from app.constants.invites import TOO_MANY_COMPANIES, TOO_MANY_INTERVIEWS


def test_limit_messages_have_translations():
    for language in TRANSLATIONS.values():
        assert TOO_MANY_COMPANIES in language
        assert TOO_MANY_INTERVIEWS in language
