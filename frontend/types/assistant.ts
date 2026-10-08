// The in-app assistant's API (services/assistant), as the panel reads it; a signed-out
// visitor's answers come from rounds' help chat.
import type { SignInProvider } from "@/types/sign-in"

/** What the panel shows under an answer for one tool's result: its items, each with the page
 * it opens (null when the service couldn't build one), or for "link" one page; or the sign-in
 * card the help chat sends a visitor who asked to sign in. */
export type AssistantBlock = {
  kind:
    | "candidate_rows"
    | "scorecard_summary"
    | "interview"
    | "credits"
    | "link"
    | "sign_in"
    | "confirm"
  items: Record<string, unknown>[]
  links: (string | null)[]
  // A sign-in card's way to sign in first: the one the visitor asked for.
  provider?: SignInProvider | null
} & Partial<ActionCard>

/** An action the assistant prepared, as its confirmation card shows it: exactly what runs
 * (`preview`), whether it can't be undone, and where it stands. "running" is the panel's own,
 * while a confirm is on its way. */
export type ActionCard = {
  action_id: string
  tool: string
  preview: Record<string, string | number | boolean>
  company_id: string | null
  destructive: boolean
  state: "pending" | "running" | "done" | "failed" | "cancelled"
  // Why it failed, in the user's language.
  detail?: string | null
}

export type ToolProgress = {
  name: string
  state: "running" | "done" | "failed"
  label: string
}

/** One server-sent event of an answer; the error event throws instead (lib/chat.ts). */
export type AssistantEvent = {
  conversation?: { id: string }
  tool?: ToolProgress
  block?: AssistantBlock
  delta?: string
  done?: { message_id: string }
  // A confirmed action's card, in its new state.
  action?: AssistantBlock
  // The user asked to sign out: the panel does it.
  sign_out?: boolean
  // The conversation's new title, for the history.
  title?: string
}

export type AssistantMessage = {
  id: string
  role: "user" | "assistant"
  source: "text" | "voice"
  content: string
  blocks: AssistantBlock[]
  status: "complete" | "cancelled" | "failed"
  created_at: string
}

export type Conversation = {
  id: string
  company_id: string | null
  title: string
  created_at: string
  updated_at: string
}

export type ConversationDetail = Conversation & {
  messages: AssistantMessage[]
}

/** The limits the panel keeps to (GET /config). */
export type AssistantConfig = {
  max_message_length: number
  // A chat older than this isn't brought back after a reload.
  restore_minutes: number
  max_audio_seconds: number
  messages_per_hour: number
  messages_per_day: number
}

/** A message as the panel shows it while it's being written, or as it was saved. */
export type ChatMessage = {
  role: "user" | "assistant"
  content: string
  blocks: AssistantBlock[]
  // A question: typed or spoken.
  source?: "text" | "voice"
  // An answer's tools so far, by their progress labels.
  progress?: string[]
  // An answer that failed, with what to show and whether a retry can fix it.
  error?: string
}
