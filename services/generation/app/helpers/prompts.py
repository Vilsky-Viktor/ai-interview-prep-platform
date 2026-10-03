from prepza_common.constants import DEFAULT_LANGUAGE, LANGUAGES


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def language_name(code: str | None) -> str:
    """The language content is written in, as prompts name it. Older runs had none: English."""
    return LANGUAGES.get(code or DEFAULT_LANGUAGE, LANGUAGES[DEFAULT_LANGUAGE])
