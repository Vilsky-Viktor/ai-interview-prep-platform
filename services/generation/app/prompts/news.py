from prepza_common.constants import MAX_NEWS_TEXT_LENGTH, MAX_NEWS_TITLE_LENGTH

NEWS_TRANSLATION_PROMPT = f"""Translate this post from prepza's news page from English into \
{{language}}.

prepza is a hiring platform: companies test job candidates with skills tests and AI interviews,
and anyone can practice for free.

Rules:
- Translate the meaning, not the words. Write what a native speaker who works in hiring and HR
  would write, with the terms that language normally uses for candidates, hiring, tests,
  interviews and practice. Avoid literal translations that change or narrow the meaning, such as
  a word for "candidate" that also means an election candidate.
- Keep "prepza" exactly as written, in lowercase, and keep product, company and ATS names (for
  example Workable, Greenhouse, Slack) as they are.
- Keep the tone, and keep the text's paragraphs and line breaks.
- Address the reader the same way throughout, as prepza's interface does in that language (in
  German, with "du").
- Plain text only: no Markdown, no HTML, no quotation marks around the result.
- The title must be at most {MAX_NEWS_TITLE_LENGTH} characters and the text at most \
{MAX_NEWS_TEXT_LENGTH} characters. If a translation would be longer, say the same more briefly.

Title:
{{title}}

Text:
{{text}}
"""
