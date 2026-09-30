import { PASSING_SCORE } from "@/constants/rounds"
import type { ReviewItem, TopicPass } from "@/types/round"

export function answerText(item: ReviewItem) {
  const answer = item.answer

  if (!answer) {
    return null
  }

  if (answer.option_index !== null && item.options) {
    return item.options[answer.option_index]
  }

  return answer.text
}

export function isPreparationDone(topicCount: number, passedCount: number) {
  return topicCount > 0 && passedCount >= topicCount
}

export function scorePassed(score: number) {
  return score >= PASSING_SCORE
}

export function topicCertificate(passes: TopicPass[]) {
  return passes.find((item) => item.certificate_id)?.certificate_id ?? null
}

/** A topic is mastered once it has a certificate, the same rule everywhere. */
export function topicMastered(passes: TopicPass[]) {
  return topicCertificate(passes) !== null
}

export function verdict(correct: boolean | null, score: number) {
  if (correct === null) {
    return `${score}%`
  }

  return correct ? "Correct" : "Incorrect"
}
