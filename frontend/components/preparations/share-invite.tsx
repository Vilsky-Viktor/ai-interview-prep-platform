"use client"

import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useEffect, useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/components/auth-provider"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { Button } from "@/components/ui/button"
import { ApiError, apiFetch } from "@/lib/api"
import type { ShareInvite as Invite } from "@/types/sharing"

export function ShareInvite({ token }: { token: string }) {
  const t = useTranslations("share")
  const router = useRouter()
  const { user, loading } = useAuth()
  const [invite, setInvite] = useState<Invite | null>(null)
  const [missing, setMissing] = useState(false)
  const [accepting, setAccepting] = useState(false)

  useEffect(() => {
    if (user) {
      apiFetch<Invite>(`/library/shares/${token}`)
        .then(setInvite)
        .catch(() => setMissing(true))
    }
  }, [user, token])

  async function accept() {
    if (!invite) {
      return
    }

    setAccepting(true)

    try {
      await apiFetch(`/library/shares/${token}/accept`, { method: "POST" })
      router.push(`/preparations/${invite.preparation_id}`)
    } catch (error) {
      const forbidden = error instanceof ApiError && error.status === 403
      toast.error(forbidden ? t("wrongEmail") : t("acceptFailed"))
      setAccepting(false)
    }
  }

  if (!loading && !user) {
    return <SignInPrompt message={t("signIn")} />
  }

  if (missing) {
    return (
      <p className="py-24 text-center text-base text-muted-foreground">
        {t("invalid")}
      </p>
    )
  }

  if (!invite) {
    return null
  }

  const matches = user?.email?.toLowerCase() === invite.email

  return (
    <div className="w-full space-y-8 text-center">
      <div className="space-y-4">
        <p className="text-base text-muted-foreground">{t("invitedToJoin")}</p>
        <h1 className="font-heading text-4xl font-medium tracking-tight text-balance normal-case sm:text-5xl">
          {invite.title}
        </h1>
      </div>
      {invite.accepted && matches ? (
        <Button
          className="h-12 px-6 text-base"
          onClick={() => router.push(`/preparations/${invite.preparation_id}`)}
        >
          {t("open")}
        </Button>
      ) : matches ? (
        <Button
          className="h-12 px-6 text-base"
          disabled={accepting}
          onClick={accept}
        >
          {t("join")}
        </Button>
      ) : (
        <p className="text-base text-muted-foreground">{t("mismatch")}</p>
      )}
    </div>
  )
}
