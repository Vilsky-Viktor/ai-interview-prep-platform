"use client"

import { useEffect, useState } from "react"

import { TopicProgress } from "@/components/rounds/topic-progress"
import { apiFetch } from "@/lib/api"
import type { Round, TopicProgress as Progressed } from "@/types/round"

/** How a finished round compares with the previous one, and where the topic now stands. */
export function RoundChange({ round }: { round: Round }) {
  const [previous, setPrevious] = useState<Round | null | undefined>(undefined)
  const [progress, setProgress] = useState<Progressed | undefined>(undefined)

  useEffect(() => {
    apiFetch<Round[]>(`/rounds/topics/${round.topic_id}/rounds`)
      .then((rounds) =>
        // Newest first, so the first other finished round is the previous one.
        setPrevious(
          rounds.find(
            (item) => item.id !== round.id && item.status === "finished"
          ) ?? null
        )
      )
      .catch(() => setPrevious(null))
    apiFetch<Progressed[]>(
      `/rounds/preparations/${round.preparation_id}/progress`
    )
      .then((rows) =>
        setProgress(rows.find((row) => row.topic_id === round.topic_id))
      )
      .catch(() => {})
  }, [round.id, round.topic_id, round.preparation_id])

  const change =
    previous?.final_score != null && round.final_score != null
      ? round.final_score - previous.final_score
      : null
  const answered = Math.min(progress?.answered ?? 0, round.total)

  return (
    <div className="mx-auto w-full max-w-md space-y-6">
      {previous !== undefined && (
        <p className="text-2xl font-medium">
          {change === null
            ? "Your first round on this topic"
            : change === 0
              ? "Same as your last round"
              : `${change > 0 ? "+" : "−"}${Math.abs(change)} points since your last round`}
        </p>
      )}
      {progress !== undefined && (
        <div className="space-y-2">
          <TopicProgress progress={progress} total={round.total} />
          <p className="text-sm text-muted-foreground tabular-nums">
            Topic: {answered} of {round.total} questions answered
          </p>
        </div>
      )}
    </div>
  )
}
