import type { ReviewItem } from "@/types/round"

export function answerText(item: ReviewItem) {
  return item.answer ? item.options[item.answer.option_index] : null
}

/** The right option's text, once the question is answered and the key may be shown. */
export function correctText(item: ReviewItem | undefined) {
  return item?.correct_option_index != null
    ? item.options[item.correct_option_index]
    : null
}

/** `correct` is null when a candidate may not see results. */
export function verdict(correct: boolean | null) {
  if (correct === null) {
    return "Answered"
  }

  return correct ? "Correct" : "Incorrect"
}
