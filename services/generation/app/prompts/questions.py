QUESTIONS_PROMPT = """Write multiple-choice interview questions on the subtopic below, each with
its answer options. The candidate sees the question with four short options and answers by
picking one of them.

For each question produce:
- question: the question itself.
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
- Vary difficulty around the given level (some easier, most at level, some harder).
- Every question covers a different angle; no rephrasings of the same question.
- Each question is self-contained and answerable without extra context.
- Never list choices (A., B., C., D.) in the question text, and do not add numbering.
- Write questions as plain sentences. Only when a question must show multi-line text whose
  layout matters, such as a program, query or config file, put it after the sentence in a
  fenced Markdown block (``` ... ```) with real line breaks and indentation.
- A program with more than one statement, or any if/elif/else, loop or function, always goes
  in a fenced block with one statement per line, even when it is short. Never squeeze it onto
  one line of the sentence.
- Write formulas and short expressions inline in plain text with proper symbols
  (for example a² + b² = c², ≤, √, π), not in a block.
- Mostly ask about the given focus.
- The topic already has the questions listed at the end. Do not repeat or rephrase them.

Option rules:
- Distractors are plausible: common misconceptions or near-misses, not absurd or joke answers.
- Distractors are clearly wrong to someone who knows the topic; exactly one option is correct.
- Similar length, tone, and specificity as correct_option; the correct option must not be
  recognizable by being the longest or most detailed.
- No "all of the above", "none of the above", or options that overlap with the correct one.
- A distractor must be wrong for the question exactly as written, not merely less precise. If
  an expert could defend it as a correct answer, it is not a distractor.

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
