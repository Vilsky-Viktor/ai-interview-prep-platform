ANSWERS_PROMPT = """{company_block}Level: {level}
Topic: {topic}

For each interview question below, produce:
- answer: the correct answer as a strong candidate would give it. Accurate, specific, and
  concise (3-5 sentences). Include key terms, trade-offs, or a concrete example where relevant.
- correct_option: the same correct answer condensed into ONE short sentence.
- distractors: exactly {distractors} incorrect options for a multiple-choice question.

Distractor rules:
- Plausible: reflect common misconceptions or near-misses, not absurd or joke answers.
- Clearly wrong to someone who knows the topic; there must be exactly one correct option.
- Similar length, tone, and specificity as correct_option; the correct option must not be
  recognizable by being the longest or most detailed.
- No "all of the above", "none of the above", or options that overlap with the correct one.

Use the exact id in brackets for each item.

Questions:
{questions}
"""
