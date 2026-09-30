REGENERATE_PROMPT = """Level: {level}

Main topic: {topic}
Subtopics: {subtopics}

Write ONE new interview question for this topic. It replaces a question the interviewer
did not like, so it must be clearly different from every existing question below.

Rules:
- Do not repeat, rephrase or narrow down any existing question; cover a different angle.
- Keep it at the given level, self-contained and answerable without extra context.
- Do not add numbering.

Existing questions:
{existing}
"""
