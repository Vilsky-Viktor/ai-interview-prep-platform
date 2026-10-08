import { SAVED_CHAT_KEY, SAVED_VISITOR_CHAT_KEY } from "@/constants/assistant"
import type { ChatMessage } from "@/types/assistant"

/** The panel as it was before a reload: open or not, and the conversation it showed (signed in)
 * or the visitor's messages (signed out). */
export type SavedChat = {
  open?: boolean
  conversationId?: string | null
  messages?: ChatMessage[]
  // The company picked in the panel (null: all companies), on the page's company it was picked
  // on (null: a page without one).
  choice?: { page: string | null; company: string | null }
}

function store(signedIn: boolean) {
  return signedIn ? localStorage : sessionStorage
}

function key(signedIn: boolean) {
  return signedIn ? SAVED_CHAT_KEY : SAVED_VISITOR_CHAT_KEY
}

/** The saved panel for the signed-in user or the visitor; empty when there's none, it doesn't
 * read right, or storage is blocked (a private window). */
export function readChat(signedIn: boolean): SavedChat {
  try {
    const value = JSON.parse(store(signedIn).getItem(key(signedIn)) ?? "null")

    return value && typeof value === "object" && !Array.isArray(value)
      ? value
      : {}
  } catch {
    return {}
  }
}

/** Keeps `change` on top of what's saved; nothing happens when storage is blocked. */
export function saveChat(signedIn: boolean, change: SavedChat) {
  try {
    const next = { ...readChat(signedIn), ...change }
    store(signedIn).setItem(key(signedIn), JSON.stringify(next))
  } catch {
    // The panel simply isn't restored.
  }
}

/** Forgets the visitor's chat, or both (signing out). */
export function clearChat(both: boolean) {
  for (const signedIn of both ? [true, false] : [false]) {
    try {
      store(signedIn).removeItem(key(signedIn))
    } catch {
      // Nothing was kept.
    }
  }
}

/** Whether the panel was open before the reload: signed in, or as the visitor who was signing
 * in. */
export function wasOpen(signedIn: boolean) {
  return Boolean(readChat(false).open || (signedIn && readChat(true).open))
}
