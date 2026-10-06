import { apiFetch } from "@/lib/api"
import type { PracticeStart } from "@/types/round"

/** Starts a practice round on the template; returns the first section's page. */
export async function startPracticeRound(templateId: string): Promise<string> {
  const round = await apiFetch<PracticeStart>(
    `/rounds/practice/${templateId}`,
    {
      method: "POST",
    }
  )

  return `/sessions/${round.session_id}`
}
