import re

# Words that name a technology, a standard or a field: prompts must work for any domain.
FIELD_TERMS = (
    "debug",
    "software",
    "engineer",
    "code",
    "technical",
    "technology",
    "program",
    "sql",
    "query",
    "shell",
    "spreadsheet",
    "regular expression",
    "regex",
    "python",
    "javascript",
    "typescript",
    "rust",
    "decorator",
    "transaction",
    "database",
    "ifrs",
    "gaap",
    "crm",
    "salesforce",
    "hubspot",
    "seo",
    "marketing",
    "accounting",
    "nursing",
    "keyword",
)


def test_generation_prompts_name_no_technology_standard_or_field():
    from app.prompts.answers import ANSWERS_PROMPT, MULTI_ANSWER_KIND
    from app.prompts.code_languages import CODE_LANGUAGES_PROMPT
    from app.prompts.extraction import EXTRACTION_SYSTEM, TEMPLATE_TITLE_RULE
    from app.prompts.questions import QUESTIONS_PROMPT
    from app.prompts.regenerate import REGENERATE_PROMPT, REPORT_GUIDANCE, REPORTS
    from app.prompts.topics import REVISION_PROMPT, TOPICS_PROMPT
    from app.prompts.verify import CONFIRM_PROMPT, SELF_CHECK_PROMPT, VERIFY_PROMPT
    from app.schemas.questions import EXAMPLE, EXAMPLE_LANGUAGE

    prompts = [
        ANSWERS_PROMPT,
        MULTI_ANSWER_KIND,
        CODE_LANGUAGES_PROMPT,
        EXTRACTION_SYSTEM,
        TEMPLATE_TITLE_RULE,
        QUESTIONS_PROMPT,
        REGENERATE_PROMPT,
        REPORTS,
        *REPORT_GUIDANCE.values(),
        TOPICS_PROMPT,
        REVISION_PROMPT,
        VERIFY_PROMPT,
        CONFIRM_PROMPT,
        SELF_CHECK_PROMPT,
        EXAMPLE,
        EXAMPLE_LANGUAGE,
    ]

    for prompt in prompts:
        for term in FIELD_TERMS:
            assert not re.search(rf"\b{term}", prompt.lower()), term

        # Task wording, never a persona.
        assert "you are" not in prompt.lower()

    assert "multiple-choice" in QUESTIONS_PROMPT
    assert "multiple-choice" in REGENERATE_PROMPT
    assert "3-5 sentences" not in ANSWERS_PROMPT


def test_about_a_third_of_the_questions_on_formal_material_come_with_a_short_example():
    from app.prompts.question_rules import PRACTICE_GUIDE, READING_RULES
    from app.prompts.questions import QUESTIONS_PROMPT

    prompt = QUESTIONS_PROMPT.format(
        level="hard",
        topic="T",
        subtopic="S",
        focus="F",
        count=9,
        multi=1,
        examples=3,
        options=4,
        max_chars=100,
        existing="None",
        language="English",
    )

    assert "about a third" in PRACTICE_GUIDE and "at least a third" not in PRACTICE_GUIDE
    assert "exactly 3 of the 9 come with an example" in " ".join(prompt.split())
    # One minute to read and answer; a minute and a half only for the hardest.
    assert "within one minute" in READING_RULES
    assert "up to a minute and a half, never more" in " ".join(READING_RULES.split())
    assert "never because of its length" in READING_RULES
