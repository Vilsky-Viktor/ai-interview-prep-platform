"use client"

import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { CHAT_APPS } from "@/components/chat-apps"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { MAX_EMAIL_LENGTH } from "@/constants/limits"
import { ApiError, apiFetch } from "@/lib/api"
import { fileBase64 } from "@/lib/files"
import { useOrigin } from "@/lib/origin"

const CHAT_BUTTON =
  "size-12 shrink-0 text-muted-foreground hover:text-foreground"

/** Sends a PDF report by email from prepza (a reply goes to the member), or a text
 * summary through a chat app (WhatsApp, Telegram, Viber, LINE), which can't carry a file. Laid out like "new candidate". */
export function ShareReport({
  open,
  onOpenChange,
  path,
  summary,
  makePdf,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  // The API path that emails the report.
  path: string
  // The chat message, for the chat apps.
  summary: string
  makePdf: () => Promise<File | null>
}) {
  const t = useTranslations("report")
  const common = useTranslations("common")
  const origin = useOrigin()
  const [email, setEmail] = useState("")
  const [sending, setSending] = useState(false)

  async function send(event: React.FormEvent) {
    event.preventDefault()
    setSending(true)

    try {
      const file = await makePdf()

      if (!file) {
        return
      }

      await apiFetch(path, {
        method: "POST",
        body: JSON.stringify({ email, pdf: await fileBase64(file) }),
      })
      toast.success(t("sent", { email }))
      setEmail("")
      onOpenChange(false)
    } catch (error) {
      // Too many emails: the API's message says when to try again.
      // Too many emails, or nothing to report yet: the API's message says why.
      const explained =
        error instanceof ApiError &&
        (error.status === 429 || error.status === 409)
      toast.error(explained ? error.message : t("sendFailed"))
    } finally {
      setSending(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={(next) => !sending && onOpenChange(next)}>
      <DialogContent showCloseButton={false} className="sm:max-w-xl">
        {/* The title on the left; the chat apps at the end of its row. */}
        <DialogHeader className="flex-row items-center justify-between gap-4">
          <DialogTitle>{t("shareTitle")}</DialogTitle>
          {/* Chats can't carry the PDF, so they get a text summary. */}
          <div className="flex items-center gap-1">
            <span className="me-2 text-sm text-muted-foreground lowercase">
              {t("orSummary")}
            </span>
            {CHAT_APPS.map(({ name, Icon, link }) => (
              <Button
                key={name}
                variant="ghost"
                size="icon"
                className={CHAT_BUTTON}
                aria-label={name}
                render={
                  <a
                    href={link(summary, origin)}
                    target="_blank"
                    rel="noopener noreferrer"
                  />
                }
                nativeButton={false}
              >
                <Icon className="size-8" />
              </Button>
            ))}
          </div>
        </DialogHeader>
        <form id="share-report-form" onSubmit={send}>
          <div className="rounded-full border border-transparent transition-colors focus-within:border-ring">
            <Input
              type="email"
              required
              maxLength={MAX_EMAIL_LENGTH}
              placeholder="manager@example.com"
              aria-label={t("recipient")}
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="h-16 border-0 px-6 text-lg focus-visible:ring-0 md:text-lg"
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
            form="share-report-form"
            className="h-10 px-5 text-base"
            disabled={sending || !email}
          >
            {/* PDF keeps its capitals inside the lowercase button; one span keeps the spacing. */}
            <span>
              {t.rich("send", {
                name: (chunks) => <span className="normal-case">{chunks}</span>,
              })}
            </span>
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
