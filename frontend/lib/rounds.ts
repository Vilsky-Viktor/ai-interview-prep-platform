import type { ReviewItem } from "@/types/round"

export function answerText(item: ReviewItem) {
  // A timed question that ran out has no option picked.
  return item.answer?.option_index != null
    ? item.options[item.answer.option_index]
    : null
}

/** The message key for an answer's verdict; `correct` is null when a candidate may not see
results. */
export function verdict(correct: boolean | null) {
  if (correct === null) {
    return "answered"
  }

  return correct ? "correct" : "incorrect"
}
