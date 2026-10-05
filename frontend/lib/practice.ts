import { apiFetch } from "@/lib/api"
import type { PracticeStart, TalentLink } from "@/types/round"

export const TALENT_LINK_PATH = "/rounds/talent-link"

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

/** Whether the signed-in talent has answered the one question about being suggested. */
export async function answeredSuggest(): Promise<boolean> {
  const link = await apiFetch<TalentLink>(TALENT_LINK_PATH)

  return link.decided
}

/** Saves the talent's answer: a link to be suggested, or null to decline or withdraw. */
export function saveTalentLink(url: string | null): Promise<TalentLink> {
  return apiFetch<TalentLink>(TALENT_LINK_PATH, {
    method: "PUT",
    body: JSON.stringify({ url }),
  })
}
