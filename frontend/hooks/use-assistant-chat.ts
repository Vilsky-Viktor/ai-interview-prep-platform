"use client"

import { usePathname } from "next/navigation"
import { useTranslations } from "next-intl"
import { useEffect, useRef, useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/components/auth-provider"
import { apiErrorMessage } from "@/lib/api"
import { getConversation, streamAssistant } from "@/lib/assistant"
import { clearChat, readChat, saveChat } from "@/lib/assistant-storage"
import { StreamError, streamHelp } from "@/lib/chat"
import { firebaseAuth } from "@/lib/firebase"
import type { AssistantEvent, ChatMessage } from "@/types/assistant"
import type { HelpMessage } from "@/types/help"

// The service's error code for a token it stopped taking mid-answer.
const SESSION_EXPIRED = "session_expired"

/** The conversation as the FAQ's help chat reads it: the questions and the answers that came. */
function helpConversation(messages: ChatMessage[]): HelpMessage[] {
  return messages
    .filter((message) => message.content && !message.error)
    .map(({ role, content }) => ({ role, content }))
}

/** The assistant's conversation in the panel: its messages, the answer streaming into the last
 * one. Each message goes with the company picked in the panel (`company`; null: all of them).
 * Signed out, the FAQ's help chat answers instead: the conversation lives only here (and in the
 * tab's sessionStorage). A reload brings back the conversation it showed; a visitor who signs in
 * keeps their chat, which the first message then saves as the start of a conversation. */
export function useAssistantChat(company: string | null, signedIn: boolean) {
  const t = useTranslations("assistant")
  const pathname = usePathname()
  const { user, loading } = useAuth()
  // Who the panel was restored for: undefined until the page knows, null for a visitor.
  const uid = loading ? undefined : (user?.uid ?? null)
  const restoredFor = useRef<string | null | undefined>(undefined)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [streaming, setStreaming] = useState(false)
  const stream = useRef<AbortController | null>(null)

  useEffect(() => () => stream.current?.abort(), [])

  // A visitor's chat is kept for a reload, once each answer is done (and only once what a
  // reload kept was brought back, so it isn't overwritten first).
  useEffect(() => {
    if (restoredFor.current !== undefined && !signedIn && !streaming) {
      saveChat(false, { messages })
    }
  }, [signedIn, streaming, messages])

  useEffect(() => {
    if (uid === undefined || restoredFor.current === uid) {
      return
    }

    const before = restoredFor.current
    restoredFor.current = uid
    void restore(before, uid)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [uid])

  /** After the page learns who's signed in: on its first load, the conversation the panel
   * showed (or the visitor's chat, while signing in); signing out or another account starts
   * over; a visitor who just signed in keeps their chat on screen. */
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

    const saved = now ? readChat(true).conversationId : null

    if (saved) {
      await open(saved, true)

      return
    }

    const visitor = readChat(false).messages

    if (Array.isArray(visitor) && visitor.length > 0) {
      setMessages(visitor)
    }
  }

  // The answer being written is always the last message.
  function updateAnswer(change: (answer: ChatMessage) => ChatMessage) {
    setMessages((current) => [...current.slice(0, -1), change(current.at(-1)!)])
  }

  function apply(event: AssistantEvent) {
    const { tool, block, delta } = event

    if (tool) {
      updateAnswer((answer) => ({
        ...answer,
        progress: [...new Set([...(answer.progress ?? []), tool.label])],
      }))
    }

    if (block) {
      updateAnswer((answer) => ({
        ...answer,
        blocks: [...answer.blocks, block],
      }))
    }

    if (delta) {
      updateAnswer((answer) => ({
        ...answer,
        content: answer.content + delta,
      }))
    }
  }

  /** Asks `text`, after `earlier` (the conversation without a failed attempt). A token the
   * service stopped taking is refreshed and the message sent again, once. */
  async function ask(
    text: string,
    source: "text" | "voice",
    earlier: ChatMessage[],
    conversation: string | null,
    resent = false
  ) {
    const question: ChatMessage = {
      role: "user",
      content: text,
      blocks: [],
      source,
    }
    const answer: ChatMessage = { role: "assistant", content: "", blocks: [] }
    setMessages([...earlier, question, answer])
    setStreaming(true)
    stream.current = new AbortController()
    const { signal } = stream.current
    let created = conversation

    try {
      if (!signedIn) {
        await streamHelp(
          helpConversation([...earlier, question]),
          apply,
          signal
        )
      } else {
        await streamAssistant(
          {
            message: text,
            source,
            page: pathname,
            ...(company && { company_id: company }),
            // A new conversation starts with what the user asked before signing in.
            ...(conversation
              ? { conversation_id: conversation }
              : { earlier: helpConversation(earlier) }),
          },
          (event) => {
            if (event.conversation) {
              created = event.conversation.id
              setConversationId(created)
              saveChat(true, { conversationId: created })
              clearChat(false)
            }

            apply(event)
          },
          signal
        )
      }
    } catch (error) {
      if (signal.aborted) {
        setStreaming(false)

        return
      }

      if (
        error instanceof StreamError &&
        error.code === SESSION_EXPIRED &&
        !resent
      ) {
        await (await firebaseAuth()).currentUser?.getIdToken(true)

        return ask(text, source, earlier, created, true)
      }

      const message =
        error instanceof StreamError
          ? error.message
          : apiErrorMessage(error, t("failed"))
      updateAnswer((current) => ({ ...current, error: message }))
    }

    setStreaming(false)
  }

  function send(text: string, source: "text" | "voice" = "text") {
    return ask(text.trim(), source, messages, conversationId)
  }

  /** Asks the last question again, in place of its failed answer. */
  function retry() {
    const question = messages.at(-2)

    if (question) {
      const earlier = messages.slice(0, -2)
      void ask(
        question.content,
        question.source ?? "text",
        earlier,
        conversationId
      )
    }
  }

  function stop() {
    stream.current?.abort()
  }

  function startNew() {
    stop()
    setConversationId(null)
    setMessages([])
    saveChat(true, { conversationId: null })
    clearChat(false)
  }

  /** Opens one of the user's conversations, and gives its company; `quietly` (restoring after a
   * reload), one that's gone leaves the welcome without an error. */
  async function open(id: string, quietly = false): Promise<string | null> {
    stop()

    try {
      const found = await getConversation(id)
      setConversationId(found.id)
      setMessages(
        found.messages.map((message) => ({
          role: message.role,
          content: message.content,
          blocks: message.blocks,
          source: message.source,
        }))
      )
      saveChat(true, { conversationId: found.id })

      return found.company_id
    } catch (error) {
      if (quietly) {
        saveChat(true, { conversationId: null })
      } else {
        toast.error(apiErrorMessage(error, t("openFailed")))
      }

      return null
    }
  }

  return {
    conversationId,
    started: conversationId !== null || messages.length > 0,
    messages,
    streaming,
    send,
    retry,
    stop,
    startNew,
    open,
  }
}
