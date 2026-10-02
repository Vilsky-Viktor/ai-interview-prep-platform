REGENERATE_PROMPT = """Write ONE new multiple-choice interview question for the topic below.
The candidate answers by picking one of four short options. It replaces a question the
interviewer did not like, so it must be clearly different from every existing question below.

Rules:
- Exactly one clearly correct answer that can be stated concisely.
- Avoid questions that several answers could fit, such as asking for "a" tool, keyword,
  or step when several take part. Ask for the one that is specifically right.
- Never ask the candidate to write, explain, describe, list, or give an example in their own
  words.
- Do not repeat, rephrase or narrow down any existing question; cover a different angle.
- Keep it at the given level, self-contained and answerable without extra context.
- Return only the question itself. The options are written in a separate step, so never list
  choices (A., B., C., D.) in the question text, and do not add numbering.
- Write the question as plain sentences. Only when it must show multi-line text whose layout
  matters, such as a program, query or config file, put it after the sentence in a fenced
  Markdown block (``` ... ```) with real line breaks and indentation.
- A program with more than one statement, or any if/elif/else, loop or function, always goes
  in a fenced block with one statement per line, even when it is short. Never squeeze it onto
  one line of the sentence.
- Write formulas and short expressions inline in plain text with proper symbols
  (for example a² + b² = c², ≤, √, π), not in a block.

Level: {level}

Main topic: {topic}
Subtopics: {subtopics}

Existing questions:
{existing}
"""
