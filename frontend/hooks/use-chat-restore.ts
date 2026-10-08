"use client"

import { useEffect, useRef } from "react"

import { useAuth } from "@/components/auth-provider"
import { getActiveConversation, getConfig } from "@/lib/assistant"
import {
  clearChat,
  readChat,
  recentVisitorChat,
  saveChat,
} from "@/lib/assistant-storage"
import type { ChatMessage } from "@/types/assistant"

/** The panel's chat across reloads and sign-ins. On the page's first load, the recent chat
 * comes back (the service says which conversation is; a visitor's, by the window /config
 * gives), and `onRestored` hears whether one did. Signing out or another account starts over;
 * a visitor who just signed in keeps their chat on screen. A visitor's chat is kept in the tab
 * with its last message's time. */
export function useChatRestore({
  signedIn,
  streaming,
  messages,
  setMessages,
  open,
  startNew,
  onRestored,
}: {
  signedIn: boolean
  streaming: boolean
  messages: ChatMessage[]
  setMessages: (messages: ChatMessage[]) => void
  open: (id: string, quietly: boolean) => Promise<string | null | undefined>
  startNew: () => void
  onRestored: (recent: boolean) => void
}) {
  const { user, loading } = useAuth()
  // Who the panel was restored for: undefined until the page knows, null for a visitor.
  const uid = loading ? undefined : (user?.uid ?? null)
  const restoredFor = useRef<string | null | undefined>(undefined)

  // Once what a reload kept was looked at, so it isn't overwritten first.
  useEffect(() => {
    if (restoredFor.current !== undefined && !signedIn && !streaming) {
      saveChat(false, { messages, lastAt: new Date().toISOString() })
    }
  }, [signedIn, streaming, messages])

  async function restore(
    before: string | null | undefined,
    now: string | null
  ) {
    if (before) {
      clearChat(true)
      startNew()
    }

    if (before !== undefined) {
      return
    }

    onRestored(now ? await restoreConversation() : await restoreVisitor())
  }

  async function restoreConversation() {
    const found = await getActiveConversation().catch(() => null)

    return found !== null && (await open(found.id, true)) !== undefined
  }

  async function restoreVisitor() {
    const config = await getConfig().catch(() => null)
    const kept = recentVisitorChat(readChat(false), config, Date.now())

    if (kept === null) {
      clearChat(false)

      return false
    }

    setMessages(kept)

    return true
  }

  useEffect(() => {
    if (uid === undefined || restoredFor.current === uid) {
      return
    }

    const before = restoredFor.current
    restoredFor.current = uid
    void restore(before, uid)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [uid])
}
