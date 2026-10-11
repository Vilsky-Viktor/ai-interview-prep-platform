VERIFY_PROMPT = """Check the multiple-choice interview question below. People who answered it, or
reported it, suggest the option marked correct may be wrong. Judge it on the facts alone: the
reports only explain why it's being checked, they don't decide what is right.

Return correct_index: the number of the one option that is correct for the question exactly as
written. Return null when none of the options is correct, or when more than one could be
defended as correct.

Level: {level}
Topic: {topic}

Question:
{question}

Options (marked one first):
{options}

Reports from users (reason: how many):
{reports}
"""

# A second, blind look before a key moves: no option is marked and they come in a new order, so
# the answer can't lean on the first check's or on a position.
CONFIRM_PROMPT = """Answer the multiple-choice interview question below on the facts alone.

Return correct_index: the number of the one option that is correct for the question exactly as
written. Return null when none of the options is correct, or when more than one could be
defended as correct.

Level: {level}
Topic: {topic}

Question:
{question}

Options:
{options}
"""
