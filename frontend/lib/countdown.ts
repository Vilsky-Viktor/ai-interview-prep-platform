import { COUNTDOWN_WARNING_SECONDS } from "@/constants/interviews"

/** When a question's countdown turns red: its last COUNTDOWN_WARNING_SECONDS, or its last third
 * when that's shorter, so a short question isn't red the whole time. */
export function warningSeconds(questionSeconds: number) {
  return Math.min(
    COUNTDOWN_WARNING_SECONDS,
    Math.max(1, Math.floor(questionSeconds / 3))
  )
}
