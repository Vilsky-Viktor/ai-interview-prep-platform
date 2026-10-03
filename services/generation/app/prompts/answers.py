ANSWERS_PROMPT = """Write every option in {language}. Keep formulas, commands and the names of tools and
products as they are.

Level: {level}
Topic: {topic}

For each multiple-choice interview question below, produce:
- correct_option: the correct answer, as concise as possible while complete and accurate.
  Never longer than {max_chars} characters.
- distractors: exactly {distractors} incorrect options, each also at most {max_chars} characters.

Distractor rules:
- Plausible: reflect common misconceptions or near-misses, not absurd or joke answers.
- Clearly wrong to someone who knows the topic; there must be exactly one correct option.
- Similar length, tone, and specificity as correct_option; the correct option must not be
  recognizable by being the longest or most detailed.
- No "all of the above", "none of the above", or options that overlap with the correct one.
- A distractor must be wrong for the question exactly as written, not merely less precise. If
  an expert could defend it as a correct answer, it is not a distractor.

Then check each question: ambiguous is true if more than one option could be defended as a
correct answer to the question as written (for example, "Which keyword is used to handle
exceptions?" when several keywords take part). Ambiguous questions are dropped.

Use the exact id in brackets for each item.

Questions:
{questions}
"""
