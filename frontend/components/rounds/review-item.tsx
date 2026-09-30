"use client"

import { cn } from "cn"
import { useState } from "react"

import { ChatPanel } from "@/components/rounds/chat-panel"
import { Button } from "@/components/ui/button"
import { answerText, scorePassed, verdict } from "@/lib/rounds"
import type { ReviewItem as ReviewItemType } from "@/types/round"

export function ReviewItem({ item }: { item: ReviewItemType }) {
  const [chatOpen, setChatOpen] = useState(false)
  const answer = item.answer
  const good = answer && (answer.correct ?? scorePassed(answer.score))

  return (
    <li className="flex items-start gap-4 p-6">
      <span className="w-16 shrink-0 font-heading text-5xl leading-none font-light text-muted-foreground tabular-nums">
        {item.number}.
      </span>
      <div className="min-w-0 flex-1 space-y-5">
        <div className="flex items-start justify-between gap-4">
          <p className="text-xl font-medium">{item.text}</p>
          <span
            className={cn(
              "shrink-0 text-2xl font-light tabular-nums",
              !answer && "text-muted-foreground",
              answer &&
                (good
                  ? "text-green-600 dark:text-green-400"
                  : "text-red-600 dark:text-red-400")
            )}
          >
            {answer ? verdict(answer.correct, answer.score) : "Not answered"}
          </span>
        </div>

        {answer && (
          <div className="space-y-3 rounded-xl bg-muted px-5 py-4">
            <p className="text-sm text-muted-foreground">Your answer</p>
            <p className="text-lg leading-relaxed font-light whitespace-pre-wrap">
              {answerText(item)}
            </p>
            {answer.feedback && (
              <p className="text-sm leading-relaxed whitespace-pre-wrap text-muted-foreground italic">
                {answer.feedback}
              </p>
            )}
          </div>
        )}
        {item.reference_answer && (
          <div className="space-y-3 rounded-xl border px-5 py-4">
            <p className="text-sm text-muted-foreground">Reference answer</p>
            <p className="text-lg leading-relaxed font-light whitespace-pre-wrap">
              {item.reference_answer}
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
    </li>
  )
}
