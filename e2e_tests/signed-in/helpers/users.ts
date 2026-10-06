import { randomBytes } from "node:crypto"

/** A short random part, so each run's users, companies and domains are new. */
export function randomId() {
  return randomBytes(4).toString("hex")
}

/** A throwaway address for someone the tests invite. Invites are emailed, and locally they may go
 * through Resend: its test domain takes any +label and delivers to nobody (like e2e.py). */
export function throwawayEmail(label: string) {
  return `delivered+e2e-${label}-${randomId()}@resend.dev`
}

/** A throwaway address for a company owner, on a reserved domain that never receives mail. Each
 * is its own inbox: a first company's welcome credits come once per inbox, and the +labels of
 * throwawayEmail all share one. */
export function ownerEmail(domain = "example.com") {
  return `e2e-owner-${randomId()}@${domain}`
}
