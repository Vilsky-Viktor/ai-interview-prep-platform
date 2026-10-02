"use client"

import { cn } from "cn"
import { useState } from "react"

import { InlineText } from "@/components/questions/inline-text"
import { QuestionText } from "@/components/questions/question-text"
import { ChatPanel } from "@/components/rounds/chat-panel"
import { Button } from "@/components/ui/button"
import { answerText, correctText, verdict } from "@/lib/rounds"
import type { ReviewItem as ReviewItemType } from "@/types/round"

export function ReviewItem({ item }: { item: ReviewItemType }) {
  const [chatOpen, setChatOpen] = useState(false)
  const answer = item.answer

  return (
    <div className="flex items-start gap-4 p-6">
      <span className="w-16 shrink-0 font-heading text-5xl leading-none font-light text-muted-foreground tabular-nums">
        {item.number}.
      </span>
      <div className="min-w-0 flex-1 space-y-5">
        <div className="flex items-start justify-between gap-4">
          <QuestionText
            text={item.text}
            className="min-w-0 text-xl font-medium"
          />
          <span
            className={cn(
              "shrink-0 text-2xl font-light tabular-nums",
              !answer && "text-muted-foreground",
              answer &&
                (answer.correct
                  ? "text-green-600 dark:text-green-400"
                  : "text-red-600 dark:text-red-400")
            )}
          >
            {answer ? verdict(answer.correct) : "Not answered"}
          </span>
        </div>

        {answer && (
          <div className="space-y-3 rounded-xl bg-muted px-5 py-4">
            <p className="text-sm text-muted-foreground">Your answer</p>
            <p className="text-lg leading-relaxed font-light whitespace-pre-wrap">
              <InlineText text={answerText(item)} />
            </p>
          </div>
        )}
        {answer && !answer.correct && correctText(item) && (
          <div className="space-y-3 rounded-xl border px-5 py-4">
            <p className="text-sm text-muted-foreground">Correct answer</p>
            <p className="text-lg leading-relaxed font-light whitespace-pre-wrap">
              <InlineText text={correctText(item)} />
            </p>
          </div>
        )}
        {answer &&
          (chatOpen ? (
            <ChatPanel answerId={answer.answer_id} />
          ) : (
            <div className="flex justify-end">
              <Button
                variant="outline"
                className="h-12 px-6 text-base"
                onClick={() => setChatOpen(true)}
              >
                Ask a follow-up
              </Button>
            </div>
          ))}
      </div>
    </div>
  )
}
