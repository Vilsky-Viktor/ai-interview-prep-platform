from prepza_common.translations import TRANSLATIONS

from app.constants.sets import TOO_MANY_SHARES


def test_report_details_message_has_translations():
    # The validator in app/schemas/feedback.py raises it.
    for language in TRANSLATIONS.values():
        assert "Details are required for this reason." in language
        assert "Title is required" in language


def test_limit_messages_have_translations():
    for language in TRANSLATIONS.values():
        assert TOO_MANY_SHARES in language
