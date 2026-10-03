"use client"

import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useEffect, useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/components/auth-provider"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { Button } from "@/components/ui/button"
import { ApiError, apiFetch } from "@/lib/api"
import type { AdminInvite as Invite } from "@/types/company"

export function AdminInvite({ token }: { token: string }) {
  const t = useTranslations("company")
  const share = useTranslations("share")
  const router = useRouter()
  const { user, loading } = useAuth()
  const [invite, setInvite] = useState<Invite | null>(null)
  const [missing, setMissing] = useState(false)
  const [accepting, setAccepting] = useState(false)

  useEffect(() => {
    if (user) {
      apiFetch<Invite>(`/companies/members/invites/${token}`)
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
      await apiFetch(`/companies/members/invites/${token}/accept`, {
        method: "POST",
      })
      router.push("/company")
    } catch (error) {
      const forbidden = error instanceof ApiError && error.status === 403
      toast.error(forbidden ? share("wrongEmail") : share("acceptFailed"))
      setAccepting(false)
    }
  }

  if (!loading && !user) {
    return <SignInPrompt message={t("signInJoin")} />
  }

  if (missing) {
    return (
      <p className="py-24 text-center text-base text-muted-foreground">
        {share("invalid")}
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
        <p className="text-base text-muted-foreground">
          {share("invitedToJoin")}
        </p>
        <h1 className="font-heading text-4xl font-medium tracking-tight text-balance sm:text-5xl">
          {invite.company_name}
        </h1>
      </div>
      {invite.joined && matches ? (
        <Button
          className="h-12 px-6 text-base"
          onClick={() => router.push("/company")}
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
        <p className="text-base text-muted-foreground">{share("mismatch")}</p>
      )}
    </div>
  )
}
