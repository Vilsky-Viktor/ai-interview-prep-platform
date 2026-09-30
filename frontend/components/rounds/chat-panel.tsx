"use client"

import { cn } from "cn"
import { ArrowUpIcon } from "lucide-react"
import { useEffect, useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { SUBMIT_HINT } from "@/constants/keys"
import { MAX_CHAT_MESSAGE_LENGTH } from "@/constants/rounds"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import { streamChat } from "@/lib/chat"
import { isSubmitShortcut } from "@/lib/keys"
import type { ChatMessage } from "@/types/round"

export function ChatPanel({ answerId }: { answerId: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [reply, setReply] = useState<string | null>(null)

  useEffect(() => {
    apiFetch<ChatMessage[]>(`/rounds/answers/${answerId}/chat`)
      .then(setMessages)
      .catch(() => {})
  }, [answerId])

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
    } catch (error) {
      toast.error(apiErrorMessage(error, "Couldn't get a reply. Please try again."))
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
    <div className="space-y-4">
      {(messages.length > 0 || streaming) && (
        <ul className="space-y-3">
          {messages.map((message, index) => (
            <Bubble key={index} role={message.role} content={message.content} />
          ))}
          {streaming && <Bubble role="assistant" content={reply || "…"} />}
        </ul>
      )}
      <form
        onSubmit={send}
        className="relative rounded-lg border border-transparent transition-colors focus-within:border-ring"
      >
        <Textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={handleKeyDown}
          maxLength={MAX_CHAT_MESSAGE_LENGTH}
          placeholder={`Ask a follow-up question… (${SUBMIT_HINT})`}
          aria-label="Follow-up question"
          className="max-h-40 min-h-16 resize-none border-0 bg-transparent px-6 py-4 pr-20 text-lg shadow-none focus-visible:border-transparent focus-visible:ring-0 md:text-lg dark:bg-input/30"
        />
        <Button
          type="submit"
          size="icon"
          className="absolute top-3 right-3 size-10 rounded-full"
          disabled={!input.trim() || streaming}
          aria-label="Send"
        >
          <ArrowUpIcon className="size-5" />
        </Button>
      </form>
    </div>
  )
}

function Bubble({ role, content }: ChatMessage) {
  return (
    <li
      className={cn(
        "w-fit max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap",
        role === "user" ? "ml-auto bg-muted" : "bg-card"
      )}
    >
      {content}
    </li>
  )
}
