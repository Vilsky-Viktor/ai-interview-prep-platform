export type GenerationStatus =
  | "queued"
  | "running"
  | "awaiting_review"
  | "done"
  | "failed"

export type DraftTopic = {
  main_topic: string
  subtopics: string[]
}

export type Generation = {
  id: string
  kind: "preparation" | "interview"
  company_id: string | null
  status: GenerationStatus
  topics: DraftTopic[] | null
  progress: { done: number; total: number } | null
  preparation_id: string | null
  error: string | null
  cost_usd: number | null
}
