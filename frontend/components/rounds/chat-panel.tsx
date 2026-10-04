"use client"

import { ArrowUpIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useEffect, useState } from "react"
import { toast } from "sonner"

import { ChatBubble, ThinkingBubble } from "@/components/chat-bubble"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import { streamChat } from "@/lib/chat"
import { announceCreditsChanged, topUpAction } from "@/lib/credits"
import { isSubmitShortcut } from "@/lib/keys"
import type { Chat, ChatMessage } from "@/types/round"

export function ChatPanel({ answerId }: { answerId: string }) {
  const t = useTranslations("rounds")
  const common = useTranslations("common")
  const billing = useTranslations("billing")
  const router = useRouter()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [turns, setTurns] = useState<Omit<Chat, "messages"> | null>(null)
  const [input, setInput] = useState("")
  const [reply, setReply] = useState<string | null>(null)

  useEffect(() => {
    load(answerId)
  }, [answerId])

  // The free turns left come from the server, which decides what a turn costs.
  async function load(id: string) {
    try {
      const chat = await apiFetch<Chat>(`/rounds/answers/${id}/chat`)
      setMessages(chat.messages)
      setTurns(chat)
    } catch {}
  }

  async function send(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const message = input.trim()
    let full = ""
    setMessages((current) => [...current, { role: "user", content: message }])
    setInput("")
    setReply("")

    try {
      await streamChat(answerId, message, (delta) => {
        full += delta
        setReply(full)
      })
      setMessages((current) => [
        ...current,
        { role: "assistant", content: full },
      ])
      void load(answerId)
      // A paid turn changes the balance in the header.
      announceCreditsChanged()
    } catch (error) {
      toast.error(
        apiErrorMessage(error, t("replyFailed")),
        topUpAction(error, billing("topUp"), () => router.push("/top-up"))
      )
      setMessages((current) => current.slice(0, -1))
      setInput(message)
    }

    setReply(null)
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (isSubmitShortcut(event)) {
      event.preventDefault()
      event.currentTarget.form?.requestSubmit()
    }
  }

  const streaming = reply !== null

  return (
    <div className="space-y-6">
      {(messages.length > 0 || streaming) && (
        <ul className="space-y-3">
          {messages.map((message, index) => (
            <ChatBubble
              key={index}
              role={message.role}
              content={message.content}
            />
          ))}
          {streaming &&
            (reply ? (
              <ChatBubble role="assistant" content={reply} />
            ) : (
              <ThinkingBubble label={common("thinking")} />
            ))}
        </ul>
      )}
      {turns && (
        <p className="text-sm text-muted-foreground">
          {turns.free_turns_left > 0
            ? t("freeTurns", { count: turns.free_turns_left })
            : t("paidTurns", { count: turns.turn_credits })}
        </p>
      )}
      <form
        onSubmit={send}
        className="relative rounded-[2rem] border border-transparent transition-colors focus-within:border-ring"
      >
        <Textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={t("followUpPlaceholder")}
          aria-label={t("followUp")}
          className="max-h-40 min-h-16 resize-none rounded-[2rem] border-0 bg-transparent px-6 py-4 pe-20 text-lg shadow-none focus-visible:border-transparent focus-visible:ring-0 md:text-lg dark:bg-input/30"
        />
        <Button
          type="submit"
          size="icon"
          className="absolute end-3 top-3 size-10 rounded-full"
          disabled={!input.trim() || streaming}
          aria-label={common("send")}
        >
          <ArrowUpIcon className="size-5" />
        </Button>
      </form>
    </div>
  )
}
