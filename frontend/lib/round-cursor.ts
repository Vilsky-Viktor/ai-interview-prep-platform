import type { AnswerResult, NextQuestion, ReviewItem, Round } from "@/types/round"

const cursorKey = (id: string) => `prepza.round.cursor.${id}`

export function markAdvancedTo(roundId: string, questionId: string) {
  sessionStorage.setItem(cursorKey(roundId), questionId)
}

export function clearRoundCursor(roundId: string) {
  sessionStorage.removeItem(cursorKey(roundId))
}

export function advancedQuestionId(roundId: string): string | null {
  return sessionStorage.getItem(cursorKey(roundId))
}

export function resultFromReview(
  item: ReviewItem,
  round: Round
): AnswerResult | null {
  if (
    !item.answer ||
    item.answer.correct === null ||
    item.correct_option_index == null
  ) {
    return null
  }

  return {
    answer_id: item.answer.answer_id,
    correct: item.answer.correct,
    correct_option_index: item.correct_option_index,
    current_score: round.current_score ?? 0,
    passed: round.passed ?? false,
    answered: round.answered,
    total: round.total,
    option_index: item.answer.option_index,
  }
}

export function questionFromReview(item: ReviewItem): NextQuestion {
  return {
    question_id: item.question_id,
    number: item.number,
    text: item.text,
    options: item.options,
  }
}
