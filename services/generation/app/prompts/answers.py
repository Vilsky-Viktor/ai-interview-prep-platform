from app.prompts.question_rules import DISTRACTOR_RULES

ANSWERS_PROMPT = (
    """Write every option in {language}. Keep formulas, commands and the names of tools and
products as they are.

Level: {level}
Topic: {topic}

For each multiple-choice interview question below, produce:
- correct_option: the correct answer, as concise as possible while complete and accurate.
  Never longer than {max_chars} characters.
- distractors: exactly {distractors} incorrect options, each also at most {max_chars} characters.

Distractor rules:
"""
    + DISTRACTOR_RULES
    + """

Then check each question: ambiguous is true if more than one option could be defended as a
correct answer to the question as written (for example, "Which keyword is used to handle
exceptions?" when several keywords take part). Ambiguous questions are dropped.

Use the exact id in brackets for each item.

Questions:
{questions}
"""
)
