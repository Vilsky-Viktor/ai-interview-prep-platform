from app.prompts.question_rules import DISTRACTOR_RULES, MULTI_ANSWER_RULES, SINGLE_ANSWER_RULES

# What each question below is, by the kind of the one it replaces or gets new options for.
SINGLE_ANSWER_KIND = (
    "Each question below is a single-answer question: exactly one option is correct.\n"
    + SINGLE_ANSWER_RULES
)
MULTI_ANSWER_KIND = (
    "Each question below is a select-all-that-apply question: 2 or 3 of its options are "
    "correct, never all 4.\n" + MULTI_ANSWER_RULES
)

ANSWERS_PROMPT = (
    """Write every option in {language}. Keep formulas, commands and the names of tools and
products as they are.

Level: {level}
Topic: {topic}

{kind}

For each multiple-choice interview question below, produce:
- correct_options: the correct options, each as concise as possible while complete and
  accurate and never longer than {max_chars} characters.
- distractors: the incorrect options, each also at most {max_chars} characters, so that there
  are {options} options in all.

Distractor rules:
"""
    + DISTRACTOR_RULES
    + """

Then check each question: ambiguous is true if its key could be argued: for a single-answer
question, more than one option could be defended as a correct answer to the question as written
(for example, "Which tool is used in this step?" when several tools take part); for
a select-all-that-apply question, any option could be defended both as correct and as wrong.
Ambiguous questions are dropped.

Use the exact id in brackets for each item.

Questions:
{questions}
"""
)
