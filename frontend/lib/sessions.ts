import { apiFetch } from "@/lib/api"
import type { InterviewSession, SessionTopic } from "@/types/company"
import type { NextQuestion } from "@/types/round"

/** A section and its next question, or null when it has none left. */
export type Step = [InterviewSession, NextQuestion | null]

export function fetchStep(id: string): Promise<Step> {
  return Promise.all([
    apiFetch<InterviewSession>(`/rounds/sessions/${id}`),
    apiFetch<NextQuestion | null>(`/rounds/sessions/${id}/next`),
  ])
}

/** The first section the candidate hasn't finished. */
export function openTopic(topics: SessionTopic[]) {
  return topics.find((topic) => topic.status !== "finished")
}
