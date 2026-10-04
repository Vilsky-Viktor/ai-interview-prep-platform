# Rules every prompt that writes questions or their options shares (questions.py, answers.py,
# regenerate.py), so a question reads the same however it was made. Plain text without braces:
# the prompts that include them are filled with str.format.

LEVEL_GUIDE = """How hard the questions are, by level:
- basic: core ideas and terms, and applying them in simple, typical cases.
- medium: using the knowledge in realistic situations: choosing between options, predicting
  what happens, spotting a mistake, working out a result.
- hard: what a senior person is tested on: trade-offs, edge cases, diagnosing a problem from
  its symptoms, multi-step reasoning and decisions under constraints. Few questions are plain
  recall of a definition or a fact; most give a situation or an example and ask about it.
Most questions are at the given level; a few are one level easier or harder."""

PRACTICE_GUIDE = """Make them practice, not trivia. Mix these kinds, as the subtopic allows:
- A short scenario with concrete details, asking what to do, choose or expect.
- A worked example with real numbers, asking for the result or the best estimate.
- When the topic or subtopic involves anything written in a formal language (a programming
  language or its libraries, SQL or another query language, shell commands, spreadsheet
  formulas, configuration files, regular expressions), at least a third of the questions come
  with a short, concrete example and ask what it prints or returns, what it does, why it
  fails, or which change fixes it. This holds even when the subtopic sounds conceptual,
  such as joins, decorators or transactions: show a real example of it. For a query, the example
  first lists the few rows the table holds, then the query. The options are then exact
  results on one line each: the printed values, the returned rows, or the name of the error.
  Keep each example small enough that its result is certain: nothing that depends on timing,
  the order of concurrent work, random values, memory addresses, today's date or the version
  in use. A language people speak is not a formal language: a sentence to read or translate
  stays in the question itself, in quotation marks, and has no example.
- Only some questions ask what a term means or which statement is true."""

DISTRACTOR_RULES = """- Each distractor is a specific, believable mistake: a common misconception, a confusion
  with a related idea, steps in the wrong order, a typical miscalculation, or the result of a
  wrong assumption. Someone who half-knows the topic should find it tempting.
- Distractors are clearly wrong to someone who knows the topic; exactly one option is correct.
- All options have the same form: the same grammatical structure, the same kind of thing (all
  numbers, all actions, all tools) and a similar level of detail.
- The correct option must not stand out. Write it in as few words as it needs, then write each
  distractor with about the same number of words, never noticeably fewer: across a set of
  questions the correct option is the longest of the four no more often than any other.
- An option is a single line; several printed values go on that line, separated by spaces.
- No "all of the above", "none of the above", or options that overlap with the correct one.
- A distractor must be wrong for the question exactly as written, not merely less precise. If
  an expert could defend it as a correct answer, it is not a distractor."""
