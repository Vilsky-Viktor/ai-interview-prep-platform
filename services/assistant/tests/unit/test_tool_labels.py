from app.constants.tool_labels import TOOL_LABELS
from app.constants.tools import TOOLS


def test_every_tool_has_a_progress_label():
    assert set(TOOL_LABELS) == set(TOOLS)
    assert all(label.endswith("…") for label in TOOL_LABELS.values())
