"use client"

import { ScorecardMark } from "@/components/company/scorecard-review"
import { AnswerOptions } from "@/components/questions/answer-options"
import { QuestionActions } from "@/components/questions/question-actions"
import { QuestionText } from "@/components/questions/question-text"
import { VirtualList } from "@/components/virtual-list"
import type { ReviewItem } from "@/types/round"

/** A finished practice round's questions, laid out like a scorecard: each with right or wrong,
 * every option with the right one marked, and the talent's own pick. Under each, the talent
 * rates or reports it, as candidates do in a test; a reported wrong answer gets the question
 * checked and fixed. `sessionId` is the topic's section. */
export function PracticeReview({
  sessionId,
  items,
}: {
  sessionId: string
  items: ReviewItem[]
}) {
  return (
    <VirtualList
      items={items}
      getKey={(item) => item.question_id}
      estimateSize={200}
      className="divide-y rounded-2xl border"
      renderItem={(item) => (
        <div className="flex items-start gap-4 p-6">
          <span className="w-16 shrink-0 font-heading text-4xl leading-none font-light text-muted-foreground tabular-nums">
            {item.number}.
          </span>
          <div className="min-w-0 flex-1 space-y-4">
            <div className="flex items-start justify-between gap-8">
              <QuestionText
                text={item.text}
                className="min-w-0 text-lg font-light"
              />
              <ScorecardMark item={item} />
            </div>
            <AnswerOptions
              options={item.options.map((answer, index) => ({
                answer,
                correct: index === item.correct_option_index,
              }))}
              // null when unanswered or timed out: still a practice report.
              picked={item.answer?.option_index ?? null}
              className="text-base"
            />
            <QuestionActions
              basePath={`/rounds/sessions/${sessionId}/questions/${item.question_id}`}
            />
          </div>
        </div>
      )}
    />
  )
}
