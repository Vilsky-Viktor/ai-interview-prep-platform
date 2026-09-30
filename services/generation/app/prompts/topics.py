TOPICS_PROMPT = """{company_block}Level: {level}

Requirements:
{requirements}

Generate interview preparation topics.

Rules:
- Every requirement above must appear in at least one topic or subtopic. Never drop one.
- Group related requirements under one topic, but keep each specific tool, technology, or
  concept by name as its own subtopic.
- Do not limit the number of subtopics. Use as many as needed for full coverage. Maximum {max_topics} main topics
- Do not add numbering.
"""

REVISION_PROMPT = """You are revising a list of interview preparation topics.

Level: {level}

Source requirements (for context):
{requirements}

Current topics (the reviewer already removed the ones they did not want):
{current}

Reviewer instructions:
{feedback}

Rules:
- Return the FULL updated list of topics.
- Apply the instructions exactly. Change, add, or remove only what they ask for.
- Keep every topic and subtopic the instructions do not mention exactly as it is (same wording).
- Do not re-add topics that are not in the current list unless the instructions ask for them.
- New topics need a main topic and specific named subtopics.
- Maximum {max_topics} main topics. Do not add numbering.
"""
