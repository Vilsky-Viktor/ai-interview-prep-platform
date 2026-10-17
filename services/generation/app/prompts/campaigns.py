from prepza_common.constants import (
    MAX_CAMPAIGN_BUTTON_LENGTH,
    MAX_CAMPAIGN_SUBJECT_LENGTH,
    MAX_CAMPAIGN_TEXT_LENGTH,
)

from app.prompts.translations import TRANSLATION_RULES

CAMPAIGN_TRANSLATION_PROMPT = f"""Translate this email to prepza's users from English into \
{{language}}.

{TRANSLATION_RULES}
- The subject must be at most {MAX_CAMPAIGN_SUBJECT_LENGTH} characters, the text at most \
{MAX_CAMPAIGN_TEXT_LENGTH} and the button at most {MAX_CAMPAIGN_BUTTON_LENGTH}. If a translation \
would be longer, say the same more briefly.
- The text is Markdown: keep its marks (**bold**, *italic*, lists, empty lines between \
paragraphs) where they belong in the translation, and keep each link's address as it is, \
translating only the link's words.
- If there's no button, leave the button empty.

Subject:
{{subject}}

Text:
{{text}}

Button:
{{button}}
"""
