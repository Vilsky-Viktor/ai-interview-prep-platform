"use client"

import { SendIcon, Share2Icon } from "lucide-react"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { InputAction } from "@/components/input-action"
import { PublicShare } from "@/components/preparations/public-share"
import { ShareList } from "@/components/preparations/share-list"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { MAX_EMAIL_LENGTH } from "@/constants/limits"
import { ApiError, apiFetch } from "@/lib/api"
import type { Share } from "@/types/sharing"

type ShareDialogProps = {
  preparationId: string
  title: string
  isPublic: boolean
}

export function ShareDialog({
  preparationId,
  title,
  isPublic,
}: ShareDialogProps) {
  const t = useTranslations("share")
  // Bumped after each new share, so the list loads again with it at the top.
  const [version, setVersion] = useState(0)
  const [email, setEmail] = useState("")
  const [sending, setSending] = useState(false)
  const sharesPath = `/library/preparations/${preparationId}/shares`

  async function send(event: React.FormEvent) {
    event.preventDefault()
    setSending(true)

    try {
      const share = await apiFetch<Share>(sharesPath, {
        method: "POST",
        body: JSON.stringify({ email }),
      })
      setVersion((current) => current + 1)
      setEmail("")
      toast.success(t("sent", { email: share.email }))
    } catch (error) {
      const invalid = error instanceof ApiError && error.status < 500
      const limited = error instanceof ApiError && error.status === 429
      toast.error(
        limited ? error.message : invalid ? t("checkEmail") : t("failed")
      )
    } finally {
      setSending(false)
    }
  }

  return (
    <Dialog>
      <DialogTrigger render={<Button variant="outline" />}>
        <Share2Icon />
        {t("share")}
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        {isPublic ? (
          <PublicShare preparationId={preparationId} title={title} />
        ) : (
          <>
            <DialogHeader>
              <DialogTitle>{t("title")}</DialogTitle>
              <DialogDescription>{t("private")}</DialogDescription>
            </DialogHeader>
            <form onSubmit={send} className="flex">
              <InputAction
                maxLength={MAX_EMAIL_LENGTH}
                type="email"
                required
                placeholder="name@example.com"
                aria-label={t("email")}
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                action={t("send")}
                icon={<SendIcon className="size-5" />}
                disabled={sending || !email}
              />
            </form>
            <ShareList key={version} path={sharesPath} />
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}
