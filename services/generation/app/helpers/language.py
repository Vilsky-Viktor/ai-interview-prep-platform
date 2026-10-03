from prepza_common.constants import DEFAULT_LANGUAGE

from app.constants.language import CYRILLIC_SHARE


def text_language(text: str, fallback: str = DEFAULT_LANGUAGE) -> str:
    """The language to generate in: the pasted text's own, so a Russian interface can still
    make an English interview. A text without letters takes `fallback`, the interface's."""
    cyrillic = sum(1 for char in text if "а" <= char.lower() <= "я" or char.lower() == "ё")
    latin = sum(1 for char in text if "a" <= char.lower() <= "z")

    if cyrillic + latin == 0:
        return fallback

    return "ru" if cyrillic / (cyrillic + latin) >= CYRILLIC_SHARE else "en"
