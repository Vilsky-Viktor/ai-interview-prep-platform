TOPICS_PROMPT = """Generate interview preparation topics.

Rules:
- Requirements are not subtopics. Turn each one into the knowledge an interview would test:
  concepts, tools, methods and practices a candidate can be quizzed on. Never copy a
  requirement's wording.
  Examples (from different fields):
    "5+ years of backend development in Rust"
      -> "Ownership and borrowing", "Lifetimes", "Error handling with Result", "Async Rust"
    "3+ years managing B2B sales with a CRM"
      -> "Sales pipeline stages", "Lead qualification frameworks", "CRM forecasting"
- Leave out years of experience, seniority, commitment, motivation and similar phrasing; they
  can't be tested. Use only the skill they refer to.
- Every requirement's skill must be covered by at least one subtopic. Never drop one.
- Group related requirements under one topic. Keep each specific tool, method, or concept
  that a requirement names as its own subtopic.
- Do not limit the number of subtopics. Use as many as needed for full coverage.
- At most {max_topics} main topics. If the requirements need more, group related ones under a
  shared topic.
- Keep every main topic and subtopic name to about 10 words at most. If a subtopic would list
  several things, split it into separate subtopics instead.
- Do not add numbering.

Level: {level}

Requirements:
{requirements}
"""

REVISION_PROMPT = """You are re-planning interview preparation topics after a reviewer's feedback.

Produce the complete, best set of topics that covers the current topics plus everything the
instructions ask for, in at most {max_topics} main topics. Re-plan the whole list rather than
patching it: names, grouping and order may change.

Rules:
- Apply the instructions fully. Content the reviewer asks to add gets its own main topic (or
  topics). Never tuck it into a topic about something else.
- The limit of {max_topics} main topics is strict and includes the added content. If adding
  it would exceed the limit, make room: combine the most closely related current topics into
  broader topics on their shared subject. Never return more than {max_topics} main topics.
- Every main topic covers one coherent subject, and every subtopic belongs to its main topic.
  Never put unrelated subjects under one title.
- Regroup only as much as needed to fit the limit, and drop only duplicated or overly narrow
  subtopics. If everything fits, keep the current topics as they are.
- Keep the coverage of the current topics unless the instructions remove something. Do not
  bring back topics the reviewer removed unless the instructions ask for them.
- Subtopics are testable knowledge (concepts, tools, methods, practices), never copied
  requirement wording, years of experience or commitment. Rewrite any current subtopic that
  reads like a requirement into the knowledge behind it.
- Use specific named subtopics. Keep every main topic and subtopic name to about 10 words at
  most; split a longer subtopic that lists several things into separate subtopics.
- Do not add numbering.

Level: {level}

Source requirements (for context):
{requirements}

Current topics (the reviewer already removed the ones they did not want):
{current}

Reviewer instructions:
{feedback}
"""

TOO_MANY_TOPICS = """You returned {count} main topics, but the limit is {max_topics}. Return the
complete list again with at most {max_topics} main topics: combine the most closely related
topics into broader topics on their shared subject, keeping every subtopic that matters.
"""
