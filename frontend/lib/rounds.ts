import { PASSING_SCORE } from "@/constants/rounds"
import type { ReviewItem, TopicProgress } from "@/types/round"

export function answerText(item: ReviewItem) {
  return item.answer ? item.options[item.answer.option_index] : null
}

/** The right option's text, once the question is answered and the key may be shown. */
export function correctText(item: ReviewItem | undefined) {
  return item?.correct_option_index != null
    ? item.options[item.correct_option_index]
    : null
}

export function isPreparationDone(topicCount: number, masteredCount: number) {
  return topicCount > 0 && masteredCount >= topicCount
}

export function scorePassed(score: number) {
  return score >= PASSING_SCORE
}

/** A topic is mastered once it has a certificate, the same rule everywhere. */
export function topicMastered(progress: TopicProgress | undefined) {
  return Boolean(progress?.certificate_id)
}

/** `correct` is null when a candidate may not see results. */
export function verdict(correct: boolean | null) {
  if (correct === null) {
    return "Answered"
  }

  return correct ? "Correct" : "Incorrect"
}
