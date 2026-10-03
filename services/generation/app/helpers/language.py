import re

from prepza_common.constants import DEFAULT_LANGUAGE

from app.constants.language import (
    LATIN_WORDS,
    PERSIAN_LETTERS,
    RUSSIAN_LETTERS,
    SCRIPT_SHARE,
    UKRAINIAN_LETTERS,
)


def text_language(text: str, fallback: str = DEFAULT_LANGUAGE) -> str:
    """The language to generate in: the pasted text's own, so a Russian interface can still make
    an English interview. A text without letters takes `fallback`, the interface's."""
    lowered = text.lower()
    hebrew = sum(1 for char in lowered if "\u0590" <= char <= "\u05ff")
    arabic = sum(1 for char in lowered if "\u0600" <= char <= "\u06ff")
    cyrillic = sum(1 for char in lowered if "а" <= char <= "я" or char in "ёіїєґ")
    latin = sum(1 for char in lowered if "a" <= char <= "z")

    letters = hebrew + arabic + cyrillic + latin

    if letters == 0:
        return fallback

    # Hebrew and Arabic-script texts are told by their alphabet, as Cyrillic ones are.
    if max(hebrew, arabic) / letters >= SCRIPT_SHARE:
        if hebrew > arabic:
            return "he"

        return "fa" if any(char in PERSIAN_LETTERS for char in lowered) else "ar"

    if cyrillic / letters >= SCRIPT_SHARE:
        ukrainian = sum(1 for char in lowered if char in UKRAINIAN_LETTERS)
        russian = sum(1 for char in lowered if char in RUSSIAN_LETTERS)

        return "uk" if ukrainian > russian else "ru"

    words = re.findall(r"[^\W\d_]+", lowered)
    hits = {
        code: sum(1 for word in words if word in vocabulary)
        for code, vocabulary in LATIN_WORDS.items()
    }
    best = max(hits, key=hits.get)

    return best if hits[best] > 0 else DEFAULT_LANGUAGE
