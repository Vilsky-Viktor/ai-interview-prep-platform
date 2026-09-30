"use client"

import type { ReactNode } from "react"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Textarea } from "@/components/ui/textarea"
import type { DraftTopic } from "@/types/generation"

type TopicReviewProps = {
  topics: DraftTopic[]
  back: ReactNode
  onSubmit: (selected: number[], instructions: string) => Promise<void>
}

export function TopicReview({ topics, back, onSubmit }: TopicReviewProps) {
  const [selected, setSelected] = useState(() => topics.map((_, index) => index))
  const [instructions, setInstructions] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const revising =
    instructions.trim().length > 0 || selected.length !== topics.length

  function toggle(index: number, checked: boolean) {
    setSelected((current) =>
      checked
        ? [...current, index].sort((a, b) => a - b)
        : current.filter((item) => item !== index)
    )
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitting(true)
    await onSubmit(selected, instructions.trim())
    setSubmitting(false)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      <div className="space-y-2">
        <div className="relative">
          {back}
          <h1 className="font-heading text-3xl font-medium tracking-tight">
            Review your topics
          </h1>
        </div>
        <p className="text-muted-foreground">
          Uncheck topics you don&apos;t need, or describe changes. Each topic
          gets its own set of questions with answers.
        </p>
      </div>

      <ul className="divide-y rounded-2xl border">
        {topics.map((topic, index) => (
          <li key={topic.main_topic}>
            <label className="flex cursor-pointer gap-3 p-4">
              <Checkbox
                className="mt-1"
                checked={selected.includes(index)}
                onCheckedChange={(checked) => toggle(index, checked)}
              />
              <span className="space-y-1">
                <span className="block font-medium">{topic.main_topic}</span>
                <span className="block text-sm text-muted-foreground">
                  {topic.subtopics.join(" · ")}
                </span>
              </span>
            </label>
          </li>
        ))}
      </ul>

      <Textarea
        value={instructions}
        onChange={(event) => setInstructions(event.target.value)}
        placeholder="Optional: describe changes, e.g. “Add a topic on system design”"
        aria-label="Changes to the topics"
        className="min-h-20"
      />

      <div className="flex justify-end">
        <Button
          type="submit"
          size="lg"
          disabled={selected.length === 0 || submitting}
        >
          {revising ? "Apply changes" : "Approve and generate"}
        </Button>
      </div>
    </form>
  )
}
