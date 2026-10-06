VERIFY_PROMPT = """Check the multiple-choice interview question below. People who answered it, or
reported it, suggest the option marked correct may be wrong. Judge it on the facts alone: the
answer counts and reports only explain why it's being checked, they don't decide what is right.

Return correct_index: the number of the one option that is correct for the question exactly as
written. Return null when none of the options is correct, or when more than one could be
defended as correct.

Level: {level}
Topic: {topic}

Question:
{question}

Options (marked one first, with how often each was picked):
{options}

Reports from users (reason: how many):
{reports}
"""
