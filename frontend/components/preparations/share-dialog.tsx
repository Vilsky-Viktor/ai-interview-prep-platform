"use client"

import { SendIcon, Share2Icon } from "lucide-react"
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
      toast.success(`Invite sent to ${share.email}`)
    } catch (error) {
      const invalid = error instanceof ApiError && error.status < 500
      toast.error(
        invalid
          ? "Check the email address and try again."
          : "Couldn't send the invite."
      )
    } finally {
      setSending(false)
    }
  }

  return (
    <Dialog>
      <DialogTrigger render={<Button variant="outline" />}>
        <Share2Icon />
        Share
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        {isPublic ? (
          <PublicShare preparationId={preparationId} title={title} />
        ) : (
          <>
            <DialogHeader>
              <DialogTitle>Share preparation</DialogTitle>
              <DialogDescription>
                We&apos;ll email an invite link. Only that email address can
                accept it.
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={send} className="flex">
              <InputAction
                type="email"
                required
                placeholder="name@example.com"
                aria-label="Email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                action="Send"
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
