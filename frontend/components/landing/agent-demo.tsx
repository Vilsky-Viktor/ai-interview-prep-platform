"use client"

import { MicIcon } from "lucide-react"
import { useTranslations } from "next-intl"

import { ActionCard } from "@/components/assistant/action-card"
import { ChatBubble } from "@/components/chat-bubble"
import { ChatInput } from "@/components/chat-input"
import { PANEL } from "@/components/landing/section"
import { Button } from "@/components/ui/button"
import type { AssistantBlock } from "@/types/assistant"

// The card the assistant prepares for the question, as the panel shows it.
const CARD: AssistantBlock = {
  kind: "confirm",
  items: [],
  links: [],
  action_id: "demo",
  tool: "invite_candidate",
  subject: "Architect",
  preview: { email: "ann.lee@example.com", name: "Ann Lee" },
  company_id: null,
  destructive: false,
  state: "pending",
}

/** The assistant's panel as it looks after a request: the question, the card waiting for
 * Confirm, and the input with the voice button, built from the panel's own pieces. A picture:
 * nothing in it can be used. */
export function AgentDemo({ question }: { question: string }) {
  const t = useTranslations("assistant")

  return (
    <div
      inert
      className={`${PANEL} mx-auto max-w-xl space-y-4 p-5 text-start sm:px-8 sm:py-6`}
    >
      <ul>
        <ChatBubble role="user" content={question} />
      </ul>
      <ActionCard
        card={CARD}
        actions={{
          onConfirm: () => {},
          onCancel: () => {},
          busy: false,
          companyNames: {},
        }}
        onNavigate={() => {}}
      />
      <ChatInput
        value=""
        onChange={() => {}}
        onSubmit={() => {}}
        label={t("placeholder")}
        placeholder={t("placeholder")}
        streaming={false}
      >
        <Button
          type="button"
          size="icon"
          variant="ghost"
          className="size-10 rounded-full"
        >
          <MicIcon className="size-5" />
        </Button>
      </ChatInput>
    </div>
  )
}
