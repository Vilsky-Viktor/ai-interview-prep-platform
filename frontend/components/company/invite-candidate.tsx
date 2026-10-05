"use client"

import { UploadIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useRef, useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import { MAX_BULK_TEXT_LENGTH } from "@/constants/limits"
import { ApiError, apiFetch } from "@/lib/api"
import type { BulkInviteResult } from "@/types/company"

/** "New candidate" beside the test's title, opening a dialog for one email or a whole list,
 * pasted or read from a file. The API finds the emails and invites each; the ones it couldn't
 * stay in the box with the reasons under it. The candidate list (`candidatesHref`) shows the
 * invited after. */
export function InviteCandidate({
  interviewId,
  candidatesHref,
}: {
  interviewId: string
  candidatesHref: string
}) {
  const t = useTranslations("interviews")
  const share = useTranslations("share")
  const common = useTranslations("common")
  const router = useRouter()
  const fileInput = useRef<HTMLInputElement>(null)
  const [open, setOpen] = useState(false)
  const [text, setText] = useState("")
  const [skipped, setSkipped] = useState<BulkInviteResult["skipped"]>([])
  const [sending, setSending] = useState(false)

  async function send(event: React.FormEvent) {
    event.preventDefault()
    setSending(true)

    try {
      const result = await apiFetch<BulkInviteResult>(
        `/companies/interviews/${interviewId}/candidates/bulk`,
        { method: "POST", body: JSON.stringify({ text }) }
      )

      if (result.invited.length > 0) {
        toast.success(
          result.invited.length === 1
            ? share("sent", { email: result.invited[0] })
            : t("invitedMany", { count: result.invited.length })
        )
        router.refresh()
      }

      // What wasn't invited stays, to fix or send again later.
      setText(result.skipped.map((row) => row.email).join("\n"))
      setSkipped(result.skipped)

      if (result.skipped.length === 0) {
        setOpen(false)
        router.push(candidatesHref)
      }
    } catch (error) {
      // No emails in the text, or too many: the API says which.
      const invalid = error instanceof ApiError && error.status < 500
      toast.error(invalid ? error.message : share("failed"))
    } finally {
      setSending(false)
    }
  }

  async function upload(file: File | undefined) {
    if (file) {
      const read = await file.text()
      setText((current) => [current.trim(), read].filter(Boolean).join("\n"))
    }
  }

  const reasons = [...new Set(skipped.map((row) => row.reason))]

  return (
    <Dialog open={open} onOpenChange={(next) => !sending && setOpen(next)}>
      <DialogTrigger
        render={<Button className="h-12 shrink-0 px-6 text-base" />}
      >
        {t("newCandidate")}
      </DialogTrigger>
      <DialogContent showCloseButton={false} className="sm:max-w-lg">
        {/* The title on the left; reading emails from a file at the end of its row. */}
        <DialogHeader className="flex-row items-center justify-between gap-4">
          <DialogTitle>{t("newCandidate")}</DialogTitle>
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="size-12 shrink-0 text-muted-foreground hover:text-foreground"
            aria-label={t("uploadFile")}
            onClick={() => fileInput.current?.click()}
          >
            <UploadIcon className="size-6" />
          </Button>
          <input
            ref={fileInput}
            type="file"
            accept=".csv,.txt,text/csv,text/plain"
            className="hidden"
            onChange={(event) => {
              upload(event.target.files?.[0])
              event.target.value = ""
            }}
          />
        </DialogHeader>
        <form
          id="invite-candidate-form"
          onSubmit={send}
          className="-mt-2 space-y-3"
        >
          {/* One email or many: it grows as a list is pasted. */}
          <Textarea
            required
            rows={1}
            maxLength={MAX_BULK_TEXT_LENGTH}
            placeholder="candidate@example.com"
            aria-label={t("candidateEmails")}
            value={text}
            onChange={(event) => {
              setText(event.target.value)
              setSkipped([])
            }}
            className="max-h-64 min-h-16 resize-none rounded-[2rem] border-transparent px-6 py-[18px] text-lg focus-visible:border-ring focus-visible:ring-0 md:text-lg"
          />
          <p className="px-6 text-sm text-muted-foreground">
            {t("emailsHint")}
          </p>
          {reasons.length > 0 && (
            <ul className="space-y-1 px-6 text-sm text-destructive">
              {reasons.map((reason) => (
                <li key={reason}>
                  {t(`skip.${reason}`, {
                    count: skipped.filter((row) => row.reason === reason)
                      .length,
                  })}
                </li>
              ))}
            </ul>
          )}
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
            form="invite-candidate-form"
            className="h-10 px-5 text-base"
            disabled={sending || !text.trim()}
          >
            {t("invite")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
