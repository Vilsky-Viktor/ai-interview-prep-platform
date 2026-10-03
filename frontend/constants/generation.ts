import type { GenerationStatus } from "@/types/generation"

export const POLL_INTERVAL_MS = 2000
export const ACTIVE_STATUSES: GenerationStatus[] = ["queued", "running"]
