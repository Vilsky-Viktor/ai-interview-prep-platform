from prepza_common.translations import TRANSLATIONS

from app.constants.chat import SESSION_EXPIRED
from app.constants.tool_labels import TOOL_LABELS, UNKNOWN_TOOL_LABEL
from app.constants.tools import TOOLS


def test_every_tool_has_a_progress_label():
    assert set(TOOL_LABELS) == {*TOOLS, "sign_out"}
    assert all(label.endswith("…") for label in TOOL_LABELS.values())


def test_every_label_and_the_streamed_errors_are_translated():
    texts = {*TOOL_LABELS.values(), UNKNOWN_TOOL_LABEL, SESSION_EXPIRED}

    for language, messages in TRANSLATIONS.items():
        assert sorted(texts - set(messages)) == [], language
