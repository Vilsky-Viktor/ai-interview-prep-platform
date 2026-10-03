from prepza_common.translations import TRANSLATIONS

from app.constants.products import NO_CANDIDATE_CREDITS, NO_GENERATIONS


def test_messages_users_see_have_translations():
    for language in TRANSLATIONS.values():
        assert NO_CANDIDATE_CREDITS in language
        assert NO_GENERATIONS in language
