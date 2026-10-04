from app.prompts.question_rules import DISTRACTOR_RULES, LEVEL_GUIDE, PRACTICE_GUIDE

QUESTIONS_PROMPT = (
    """Write multiple-choice interview questions on the subtopic below, each with
its answer options. The candidate sees the question with four short options and answers by
picking one of them.

For each question produce:
- question: the question itself.
- example: what the question shows, if anything (see the question rules); otherwise null.
- correct_option: the correct answer, as concise as possible while complete and accurate.
  Never longer than {max_chars} characters.
- distractors: exactly {distractors} incorrect options, each also at most {max_chars} characters.
- ambiguous: true if more than one option could be defended as a correct answer to the
  question as written. Ambiguous questions are dropped.

Question rules:
- Every question has exactly one clearly correct answer that can be stated concisely.
- Avoid questions that several answers could fit, such as asking for "a" tool, keyword,
  or step when several take part. Ask for the one that is specifically right.
- Never ask the candidate to write, explain, describe, list, give an example, or walk through
  steps in their own words. Ask what is true, which choice is best, what happens next, what
  something means, or what to do first in a situation.
- Every question covers a different angle; no rephrasings of the same question.
- Each question is self-contained and answerable without extra context: it states everything
  the answer depends on, such as the starting situation, the goal being optimized, and the
  version or standard in use when the answer differs between them.
- Never list choices (A., B., C., D.) in the question text, and do not add numbering.
- Write questions as plain sentences. Text whose layout matters, such as a program, a query,
  a command, a formula or a file, never goes into the sentences: it goes into example, exactly
  as it would be typed, one statement per line, with real line breaks and indentation. It is
  shown under the question. A question that refers to an example ("this query", "the command
  below") always has one in example.
- Write formulas and short expressions inline in plain text with proper symbols
  (for example a² + b² = c², ≤, √, π), not in a block.
- Mostly ask about the given focus.
- The topic already has the questions listed at the end. Do not repeat or rephrase them.

"""
    + LEVEL_GUIDE
    + "\n\n"
    + PRACTICE_GUIDE
    + """

Option rules:
"""
    + DISTRACTOR_RULES
    + """

Write every question and option in {language}. Keep formulas, commands and the names of tools and
products as they are.

Level: {level}
Main topic: {topic}
Subtopic: {subtopic}
Focus: {focus}
Number of questions: {count}

Questions the topic already has:
{existing}
"""
)
