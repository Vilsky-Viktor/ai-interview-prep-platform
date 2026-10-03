from prepza_common.constants import CONTENT_LANGUAGES, DEFAULT_LANGUAGE


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def language_name(code: str | None) -> str:
    """The language content is written in, as prompts name it. Older runs had none: English."""
    return CONTENT_LANGUAGES.get(code or DEFAULT_LANGUAGE, CONTENT_LANGUAGES[DEFAULT_LANGUAGE])
