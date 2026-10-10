"use client"

import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useEffect, useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/components/auth-provider"
import { useSignIn } from "@/components/sign-in-dialog"
import { Button } from "@/components/ui/button"
import { WarningCard } from "@/components/warning-card"
import { ApiError, apiFetch } from "@/lib/api"
import type { AdminInvite as Invite } from "@/types/company"

export function AdminInvite({ token }: { token: string }) {
  const t = useTranslations("company")
  const share = useTranslations("share")
  const router = useRouter()
  const { user, loading } = useAuth()
  const signIn = useSignIn()
  const [invite, setInvite] = useState<Invite | null>(null)
  const [missing, setMissing] = useState(false)
  const [accepting, setAccepting] = useState(false)

  // Read signed in or not, so a visitor sees what the invitation is for before signing in;
  // again after signing in, for whose it is.
  useEffect(() => {
    if (!loading) {
      apiFetch<Invite>(`/companies/members/invites/${token}`)
        .then(setInvite)
        .catch(() => setMissing(true))
    }
  }, [loading, user, token])

  async function accept() {
    if (!invite) {
      return
    }

    setAccepting(true)

    try {
      await apiFetch(`/companies/members/invites/${token}/accept`, {
        method: "POST",
      })
      router.push("/companies")
    } catch (error) {
      const forbidden = error instanceof ApiError && error.status === 403
      toast.error(forbidden ? share("wrongEmail") : share("acceptFailed"))
      setAccepting(false)
    }
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
        <h1 className="font-heading text-4xl font-medium tracking-tight text-balance normal-case sm:text-5xl">
          {invite.company_name}
        </h1>
      </div>
      {!user ? (
        <Button className="h-12 px-6 text-base" onClick={() => signIn()}>
          {t("signInToJoin")}
        </Button>
      ) : invite.joined && matches ? (
        <Button
          className="h-12 px-6 text-base"
          onClick={() => router.push("/companies")}
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
        // Signed in with another email: a warning, in the warning card.
        <WarningCard className="mx-auto w-fit text-start">
          {share("mismatch")}
        </WarningCard>
      )}
    </div>
  )
}
