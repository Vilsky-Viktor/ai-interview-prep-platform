from app.prompts.question_rules import LEVEL_GUIDE, PRACTICE_GUIDE

REGENERATE_PROMPT = (
    """Write ONE new multiple-choice interview question for the topic below.
The candidate answers by picking one of four short options. It replaces a question the
interviewer did not like, so it must be clearly different from every existing question below.

Rules:
- Exactly one clearly correct answer that can be stated concisely.
- Avoid questions that several answers could fit, such as asking for "a" tool, keyword,
  or step when several take part. Ask for the one that is specifically right.
- Never ask the candidate to write, explain, describe, list, or give an example in their own
  words.
- Do not repeat, rephrase or narrow down any existing question; cover a different angle.
- Keep it at the given level, self-contained and answerable without extra context: it states
  everything the answer depends on, such as the starting situation, the goal being optimized,
  and the version or standard in use when the answer differs between them.
- Return only the question and, if it shows one, its example. The options are written in a
  separate step, so never list choices (A., B., C., D.) in the question text, and do not add
  numbering.
- Write the question as plain sentences. Text whose layout matters, such as a program, a query,
  a command, a formula or a file, never goes into the sentences: it goes into example, exactly
  as it would be typed, one statement per line, with real line breaks and indentation. It is
  shown under the question. A question that refers to an example ("this query", "the command
  below") always has one in example.
- Write formulas and short expressions inline in plain text with proper symbols
  (for example a² + b² = c², ≤, √, π), not in a block.

"""
    + LEVEL_GUIDE
    + "\n\n"
    + PRACTICE_GUIDE
    + """

Write every word of the question in {language}. Keep formulas, commands and the names of tools and
products as they are.

Level: {level}

Main topic: {topic}
Subtopics: {subtopics}

Existing questions:
{existing}
"""
)
