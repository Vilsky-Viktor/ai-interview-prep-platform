import type { GenerationStatus } from "@/types/generation"

export const POLL_INTERVAL_MS = 2000
export const ACTIVE_STATUSES: GenerationStatus[] = ["queued", "running"]

export const UNFINISHED_LABELS: Record<GenerationStatus, string> = {
  queued: "Generating",
  running: "Generating",
  awaiting_review: "Review topics",
  done: "Done",
  failed: "Failed",
  cancelled: "Cancelled",
}
