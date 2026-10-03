"use client"

import { cn } from "cn"
import { ChevronDownIcon, FlagIcon } from "lucide-react"
import { useTranslations } from "next-intl"
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
import { FEEDBACK_HOVER_CLASS, REPORT_REASONS } from "@/constants/feedback"
import { ApiError, apiErrorMessage, apiFetch } from "@/lib/api"
import type { ReportReason } from "@/types/feedback"

export function ReportDialog({ basePath }: { basePath: string }) {
  const t = useTranslations("questions")
  const common = useTranslations("common")
  const reasons = useTranslations("reportReasons")
  const [open, setOpen] = useState(false)
  const [reason, setReason] = useState<ReportReason | "">("")
  const [comment, setComment] = useState("")
  const [sending, setSending] = useState(false)
  const [reported, setReported] = useState(false)

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

    // Which reasons need details is the API's rule; its message shows if they're missing.
    if (!reason) {
      return
    }

    setSending(true)

    try {
      await apiFetch(`${basePath}/reports`, {
        method: "POST",
        body: JSON.stringify({ reason, comment: comment.trim() }),
      })
      toast.success(t("reported"))
      setReported(true)
      handleOpen(false)
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        setReported(true)
        handleOpen(false)

        return
      }

      toast.error(apiErrorMessage(error, t("reportFailed")))
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
            aria-label={reported ? t("questionReported") : t("report")}
            className={cn(FEEDBACK_HOVER_CLASS, "h-full w-full rounded-none")}
            aria-pressed={reported}
            disabled={reported}
          />
        }
      >
        <FlagIcon
          className={cn("size-6", reported && "fill-primary text-primary")}
        />
      </DialogTrigger>
      <DialogContent showCloseButton={false} className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{t("report")}</DialogTitle>
          <DialogDescription>{t("whatsWrong")}</DialogDescription>
        </DialogHeader>
        <form id="report-question-form" onSubmit={send} className="space-y-4">
          <div className="relative rounded-lg border border-transparent transition-colors focus-within:border-ring">
            <select
              required
              aria-label={t("reason")}
              value={reason}
              onChange={(event) =>
                setReason(event.target.value as ReportReason | "")
              }
              className={cn(
                "h-16 w-full appearance-none rounded-lg border-0 bg-transparent px-6 pr-16 text-lg outline-none dark:bg-input/30",
                !reason && "text-muted-foreground"
              )}
            >
              <option value="">{t("selectReason")}</option>
              {REPORT_REASONS.map((key) => (
                <option key={key} value={key}>
                  {reasons(key)}
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
              placeholder={t("details")}
              aria-label={t("details")}
              value={comment}
              onChange={(event) => setComment(event.target.value)}
              className="min-h-32 resize-none border-0 bg-transparent px-6 py-4 text-lg shadow-none focus-visible:border-transparent focus-visible:ring-0 md:text-lg dark:bg-input/30"
            />
          </div>
        </form>
        <DialogFooter>
          <DialogClose
            render={
              <Button
                variant="outline"
                className="h-10 px-5 text-base"
                disabled={sending}
              />
            }
          >
            {common("cancel")}
          </DialogClose>
          <Button
            type="submit"
            form="report-question-form"
            className="h-10 px-5 text-base"
            disabled={!reason || sending}
          >
            {common("send")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
