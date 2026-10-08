import { COMPANY_PATH, LINK_PAGES } from "@/constants/assistant"
import { ApiError, apiFetch, authHeaders, errorDetail } from "@/lib/api"
import { streamEvents } from "@/lib/chat"
import type {
  AssistantBlock,
  AssistantConfig,
  AssistantEvent,
  Conversation,
  ConversationDetail,
} from "@/types/assistant"

const BASE = "/assistant"

/** Sends a message to the assistant and calls onEvent with each event of its answer. */
export function streamAssistant(
  body: {
    message: string
    conversation_id?: string
    company_id?: string
    source?: "text" | "voice"
    page?: string
    earlier?: { role: "user" | "assistant"; content: string }[]
  },
  onEvent: (event: AssistantEvent) => void,
  signal: AbortSignal
) {
  return streamEvents<AssistantEvent>(`${BASE}/chat`, body, onEvent, signal)
}

export function getConfig() {
  return apiFetch<AssistantConfig>(`${BASE}/config`)
}

/** The user's stage for the welcome, about the page's company or all of theirs. */
export async function getWelcomeStage(companyId: string | null) {
  const query = companyId ? `?company_id=${companyId}` : ""

  return (await apiFetch<{ stage: string }>(`${BASE}/welcome${query}`)).stage
}

export function listConversations() {
  return apiFetch<Conversation[]>(`${BASE}/conversations`)
}

export function getConversation(id: string) {
  return apiFetch<ConversationDetail>(`${BASE}/conversations/${id}`)
}

export function deleteConversation(id: string) {
  return apiFetch<void>(`${BASE}/conversations/${id}`, { method: "DELETE" })
}

/** A voice message's text, heard in the interface's language. The recording is the body. */
export async function transcribe(audio: Blob): Promise<string> {
  const response = await fetch(`/api${BASE}/transcribe`, {
    method: "POST",
    headers: { ...(await authHeaders()), "Content-Type": audio.type },
    body: audio,
  })
  const body = await response.json().catch(() => null)

  if (!response.ok) {
    throw new ApiError(
      response.status,
      errorDetail(body) ?? `Transcription failed with status ${response.status}`
    )
  }

  return body.text
}

/** An answer's link, only to one of the app's own pages ("/…", never "//host" or a scheme);
 * null for anything else. */
export function inAppHref(href: unknown): string | null {
  if (
    typeof href !== "string" ||
    !href.startsWith("/") ||
    href.startsWith("//")
  ) {
    return null
  }

  return href.includes("\\") ? null : href
}

/** The "assistant.pages" message naming the page a link opens, or null for a page the panel
 * doesn't know. */
export function linkPage(href: string): string | null {
  return LINK_PAGES.find(([pattern]) => pattern.test(href))?.[1] ?? null
}

/** An answer's blocks as the panel shows them: rows of items, each with its page, and the pages
 * the "link" blocks lead to once each, after the rows. */
export function answerParts(blocks: AssistantBlock[]) {
  const rows = blocks
    .filter((block) => block.kind !== "link" && block.kind !== "sign_in")
    .map((block) => ({
      kind: block.kind,
      items: block.items.map((item, index) => ({
        item,
        href: inAppHref(block.links[index]),
      })),
    }))
  const links = blocks
    .filter((block) => block.kind === "link")
    .flatMap((block) => block.links.map(inAppHref))
    .filter((href): href is string => href !== null)

  const signIn = blocks.find((block) => block.kind === "sign_in")

  return { rows, links: [...new Set(links)], signIn }
}

/** The company a page is about (/companies/<id>/…), or null. */
export function pageCompany(path: string): string | null {
  return COMPANY_PATH.exec(path)?.[1] ?? null
}
