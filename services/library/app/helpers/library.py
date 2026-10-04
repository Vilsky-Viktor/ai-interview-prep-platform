from app.constants.library import LIBRARY_EXTRA_LANGUAGE


def default_languages(language: str) -> list[str]:
    """The library's languages before the reader chooses: theirs, and English."""
    return list(dict.fromkeys([language, LIBRARY_EXTRA_LANGUAGE]))
