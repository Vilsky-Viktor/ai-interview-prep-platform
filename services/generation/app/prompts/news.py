from prepza_common.constants import MAX_NEWS_TEXT_LENGTH, MAX_NEWS_TITLE_LENGTH

from app.prompts.translations import TRANSLATION_RULES

NEWS_TRANSLATION_PROMPT = f"""Translate this post from prepza's news page from English into \
{{language}}.

{TRANSLATION_RULES}
- The title must be at most {MAX_NEWS_TITLE_LENGTH} characters and the text at most \
{MAX_NEWS_TEXT_LENGTH} characters. If a translation would be longer, say the same more briefly.

Title:
{{title}}

Text:
{{text}}
"""
