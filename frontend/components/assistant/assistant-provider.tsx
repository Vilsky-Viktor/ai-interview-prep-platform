"use client"

import { createContext, useContext, useState } from "react"

import { AssistantPanel } from "@/components/assistant/assistant-panel"
import { useAuth } from "@/components/auth-provider"
import { saveChat, wasOpen } from "@/lib/assistant-storage"

// Opens or closes the assistant's panel.
const AssistantContext = createContext<() => void>(() => {})

/** The assistant's panel, mounted once for every page so its conversation survives moving
 * between them (and, as far as the browser keeps it, a reload); the header's button
 * toggles it. */
export function AssistantProvider({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false)
  const { user } = useAuth()
  const signedIn = user !== null

  function change(next: boolean) {
    setOpen(next)
    saveChat(signedIn, { open: next })

    // The visitor's chat is part of this one now.
    if (signedIn) {
      saveChat(false, { open: next })
    }
  }

  return (
    <AssistantContext value={() => change(!open)}>
      {children}
      <AssistantPanel
        open={open}
        onOpenChange={change}
        // Open again after a reload when it was open, and only with a recent chat.
        onRestored={(recent) => recent && wasOpen(signedIn) && setOpen(true)}
      />
    </AssistantContext>
  )
}

/** Opens the assistant's panel, or closes it when open. */
export function useAssistant() {
  return useContext(AssistantContext)
}
