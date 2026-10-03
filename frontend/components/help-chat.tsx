"use client"

import { ArrowUpIcon } from "lucide-react"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { ChatBubble } from "@/components/chat-bubble"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { apiErrorMessage } from "@/lib/api"
import { streamHelp } from "@/lib/chat"
import { isSubmitShortcut } from "@/lib/keys"
import type { HelpMessage } from "@/types/help"

/** The FAQ page's chat about prepza, open to visitors too. The conversation lives only here. */
export function HelpChat() {
  const t = useTranslations("faq.chat")
  const common = useTranslations("common")
  const [messages, setMessages] = useState<HelpMessage[]>([])
  const [input, setInput] = useState("")
  const [reply, setReply] = useState<string | null>(null)

  async function send(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const question: HelpMessage = { role: "user", content: input.trim() }
    const conversation = [...messages, question]
    let full = ""
    setMessages(conversation)
    setInput("")
    setReply("")

    try {
      await streamHelp(conversation, (delta) => {
        full += delta
        setReply(full)
      })
      setMessages([...conversation, { role: "assistant", content: full }])
    } catch (error) {
      toast.error(apiErrorMessage(error, t("failed")))
      setMessages(messages)
      setInput(question.content)
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
    <section className="space-y-6">
      <div className="space-y-2">
        <h2 className="font-heading text-2xl font-medium tracking-tight">
          {t("title")}
        </h2>
        <p className="text-base text-muted-foreground">{t("text")}</p>
      </div>
      <div className="space-y-6 rounded-3xl bg-card p-4 shadow-sm ring-1 ring-foreground/5 sm:p-6">
        {(messages.length > 0 || streaming) && (
          <ul className="space-y-3" aria-live="polite">
            {messages.map((message, index) => (
              <ChatBubble
                key={index}
                role={message.role}
                content={message.content}
              />
            ))}
            {streaming && (
              <ChatBubble role="assistant" content={reply || "…"} />
            )}
          </ul>
        )}
        <form
          onSubmit={send}
          className="relative rounded-[2rem] border border-transparent transition-colors focus-within:border-ring"
        >
          <Textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={t("placeholder")}
            aria-label={t("title")}
            className="max-h-40 min-h-16 resize-none rounded-[2rem] border-0 bg-muted/50 px-6 py-4 pe-20 text-lg shadow-none focus-visible:border-transparent focus-visible:ring-0 md:text-lg dark:bg-input/30"
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
    </section>
  )
}
