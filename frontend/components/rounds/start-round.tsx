"use client"

import { ArrowRightIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { MODE_HINTS, MODE_LABELS, ROUND_MODES } from "@/constants/rounds"
import { apiFetch } from "@/lib/api"
import type { Round, RoundMode } from "@/types/round"

export function StartRound({
  topicId,
  modes = ROUND_MODES,
}: {
  topicId: string
  modes?: RoundMode[]
}) {
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const [starting, setStarting] = useState(false)

  async function start(mode: RoundMode) {
    setStarting(true)

    try {
      const round = await apiFetch<Round>("/rounds/rounds", {
        method: "POST",
        body: JSON.stringify({ topic_id: topicId, mode }),
      })
      router.push(`/rounds/${round.id}`)
    } catch {
      toast.error("Couldn't start the round. Please try again.")
      setStarting(false)
    }
  }

  function onStart() {
    if (modes.length === 1) {
      start(modes[0])

      return
    }

    setOpen(true)
  }

  return (
    <>
      <Button
        size="lg"
        className="h-12 px-8 text-base"
        disabled={starting}
        onClick={onStart}
      >
        Start
      </Button>
      <Dialog
        open={open}
        onOpenChange={(next) => {
          if (!starting) {
            setOpen(next)
          }
        }}
      >
        <DialogContent showCloseButton={false} className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>How do you want to practice?</DialogTitle>
            <DialogDescription>
              Choose a question format for this round.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-2">
            {modes.map((mode) => (
              <Button
                key={mode}
                variant="outline"
                className="h-auto w-full items-center justify-between gap-4 border-0 px-4 py-3 text-left text-base whitespace-normal"
                disabled={starting}
                onClick={() => start(mode)}
              >
                <span className="flex min-w-0 flex-col items-start gap-1 text-left">
                  <span className="text-xl font-medium">{MODE_LABELS[mode]}</span>
                  <span className="text-sm font-normal whitespace-nowrap text-muted-foreground">
                    {MODE_HINTS[mode]}
                  </span>
                </span>
                <ArrowRightIcon className="size-5 shrink-0" />
              </Button>
            ))}
          </div>
          <DialogFooter>
            <DialogClose
              render={
                <Button
                  variant="outline"
                  className="h-10 px-5 text-base"
                  disabled={starting}
                />
              }
            >
              Cancel
            </DialogClose>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
