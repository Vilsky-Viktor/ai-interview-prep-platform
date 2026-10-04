"use client"

import { cn } from "cn"
import { SendIcon } from "lucide-react"
import { useEffect, useState } from "react"

import { Caret } from "@/components/landing/caret"
import { Badge } from "@/components/ui/badge"

// The demo's steps and how long each shows, in milliseconds. It starts with only the person
// already invited, which is also what shows with reduced motion; then a new invite is typed,
// sent and shown. "typing" shows one more letter of the email each `ms`.
const STEPS = [
  { name: "idle", ms: 1400 },
  { name: "typing", ms: 75 },
  { name: "send", ms: 400 },
  { name: "invited", ms: 3200 },
] as const

type Person = { email: string; joined: boolean }

/** Inviting someone to a private kit as the share dialog really does it
 * (components/preparations/share-dialog.tsx): an email typed and sent, and the new invite at
 * the top of the list. */
export function InviteDemo({
  people,
  invitee,
  labels,
}: {
  people: Person[]
  invitee: string
  labels: { joined: string; invited: string }
}) {
  const [index, setIndex] = useState(0)
  const [letters, setLetters] = useState(0)
  const step = STEPS[index].name

  useEffect(() => {
    // With reduced motion the demo doesn't play; the list stays as it starts.
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return
    }

    let at = 0
    let typed = 0
    let timer: number

    function next() {
      if (STEPS[at].name === "typing" && typed < invitee.length) {
        typed += 1
      } else {
        at = (at + 1) % STEPS.length

        if (at === 0) {
          typed = 0
        }
      }

      setIndex(at)
      setLetters(typed)
      timer = window.setTimeout(next, STEPS[at].ms)
    }

    timer = window.setTimeout(next, STEPS[0].ms)

    return () => window.clearTimeout(timer)
  }, [invitee])

  const invited = step === "invited"
  const draft =
    step === "typing" || step === "send" ? invitee.slice(0, letters) : ""
  // Newest first, as the real list shows them.
  const shown = invited
    ? [{ email: invitee, joined: false }, ...people]
    : people

  return (
    <>
      <div className="relative rounded-full bg-muted/50">
        <p className="px-6 py-4 pe-20">
          {draft ? (
            <span>
              {draft}
              <Caret />
            </span>
          ) : (
            <span className="text-muted-foreground">name@example.com</span>
          )}
        </p>
        <span
          className={cn(
            "absolute end-2.5 top-1/2 flex size-10 -translate-y-1/2 items-center justify-center rounded-full bg-primary text-primary-foreground transition-opacity",
            !draft && "opacity-50",
            step === "send" && "ring-2 ring-ring/50"
          )}
        >
          <SendIcon className="size-5" />
        </span>
      </div>
      {/* Room for the new invite below the list, so the card keeps its size while the demo
          plays; the list itself only grows when the invite arrives. */}
      <div className="min-h-[104px]">
        <ul className="space-y-2">
          {shown.map(({ email, joined }) => (
            <li
              key={email}
              className={cn(
                "flex items-center justify-between gap-2 rounded-lg px-4 py-3 transition-colors",
                invited && email === invitee
                  ? "bg-primary/10"
                  : "bg-black/5 dark:bg-black/40"
              )}
            >
              <span className="truncate">{email}</span>
              <Badge variant={joined ? "secondary" : "outline"}>
                {joined ? labels.joined : labels.invited}
              </Badge>
            </li>
          ))}
        </ul>
      </div>
    </>
  )
}
