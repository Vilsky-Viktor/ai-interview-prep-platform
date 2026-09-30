QUESTIONS_PROMPT = """{company_block}Level: {level}

Main topic: {topic}
Subtopic: {subtopic}

Write {count} distinct interview questions on this subtopic.

Rules:
- Vary difficulty around the given level (some easier, most at level, some harder).
- Mix concept, practical, debugging, trade-off, and scenario-based questions.
- Every question must cover a different angle; no rephrasings of the same question.
- Each question must be self-contained and answerable without extra context.
- Do not add numbering.
"""
