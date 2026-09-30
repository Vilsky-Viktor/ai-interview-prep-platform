"use client"

import { cn } from "cn"
import { ChevronDownIcon, FlagIcon } from "lucide-react"
import { useEffect, useState } from "react"
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
  DialogTrigger,
} from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import {
  FEEDBACK_HOVER_CLASS,
  MAX_REPORT_COMMENT_LENGTH,
  REPORT_REASONS,
} from "@/constants/feedback"
import { ApiError, apiFetch } from "@/lib/api"
import type { ReportReason } from "@/types/feedback"

export function ReportDialog({ basePath }: { basePath: string }) {
  const [open, setOpen] = useState(false)
  const [reason, setReason] = useState<ReportReason | "">("")
  const [comment, setComment] = useState("")
  const [sending, setSending] = useState(false)
  const [reported, setReported] = useState(false)
  const detailsRequired = reason === "other"

  // Callers remount this per question, so the state never carries over.
  useEffect(() => {
    apiFetch<{ reported: boolean }>(`${basePath}/reports/mine`)
      .then((body) => setReported(body.reported))
      .catch(() => {})
  }, [basePath])

  function handleOpen(next: boolean) {
    setOpen(next)

    if (!next) {
      setReason("")
      setComment("")
    }
  }

  async function send(event: React.FormEvent) {
    event.preventDefault()

    if (!reason || (detailsRequired && !comment.trim())) {
      return
    }

    setSending(true)

    try {
      await apiFetch(`${basePath}/reports`, {
        method: "POST",
        body: JSON.stringify({ reason, comment: comment.trim() }),
      })
      toast.success("Thanks, we got your report")
      setReported(true)
      handleOpen(false)
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        setReported(true)
        handleOpen(false)

        return
      }

      toast.error("Couldn't send the report. Please try again.")
    } finally {
      setSending(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpen}>
      <DialogTrigger
        render={
          <Button
            variant="ghost"
            size="icon-lg"
            aria-label={reported ? "Question reported" : "Report question"}
            className={cn(FEEDBACK_HOVER_CLASS, "h-full w-full rounded-none")}
            aria-pressed={reported}
            disabled={reported}
          />
        }
      >
        <FlagIcon className={cn("size-6", reported && "fill-primary text-primary")} />
      </DialogTrigger>
      <DialogContent showCloseButton={false} className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Report question</DialogTitle>
          <DialogDescription>What&apos;s wrong with it?</DialogDescription>
        </DialogHeader>
        <form id="report-question-form" onSubmit={send} className="space-y-4">
          <div className="relative rounded-lg border border-transparent transition-colors focus-within:border-ring">
            <select
              required
              aria-label="Report reason"
              value={reason}
              onChange={(event) =>
                setReason(event.target.value as ReportReason | "")
              }
              className={cn(
                "h-16 w-full appearance-none rounded-lg border-0 bg-transparent px-6 pr-16 text-lg outline-none dark:bg-input/30",
                !reason && "text-muted-foreground"
              )}
            >
              <option value="">Select a reason</option>
              {(Object.keys(REPORT_REASONS) as ReportReason[]).map((key) => (
                <option key={key} value={key}>
                  {REPORT_REASONS[key]}
                </option>
              ))}
            </select>
            <ChevronDownIcon
              aria-hidden
              className="pointer-events-none absolute top-1/2 right-6 size-6 -translate-y-1/2 text-muted-foreground"
            />
          </div>
          <div className="rounded-lg border border-transparent transition-colors focus-within:border-ring">
            <Textarea
              required={detailsRequired}
              placeholder={detailsRequired ? "Details" : "Details (optional)"}
              aria-label="Details"
              maxLength={MAX_REPORT_COMMENT_LENGTH}
              value={comment}
              onChange={(event) => setComment(event.target.value)}
              className="min-h-32 resize-none border-0 bg-transparent px-6 py-4 text-lg shadow-none focus-visible:border-transparent focus-visible:ring-0 md:text-lg dark:bg-input/30"
            />
          </div>
        </form>
        <DialogFooter>
          <DialogClose
            render={
              <Button variant="outline" className="h-10 px-5 text-base" disabled={sending} />
            }
          >
            Cancel
          </DialogClose>
          <Button
            type="submit"
            form="report-question-form"
            className="h-10 px-5 text-base"
            disabled={!reason || sending || (detailsRequired && !comment.trim())}
          >
            Send
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
