"use client"

import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useEffect, useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/components/auth-provider"
import { InviteIntro } from "@/components/company/invite-intro"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { Button } from "@/components/ui/button"
import { ApiError, apiErrorMessage, apiFetch } from "@/lib/api"
import type { InviteView as Invite, SessionSummary } from "@/types/company"

export function InviteView({ token }: { token: string }) {
  const t = useTranslations("invite")
  const share = useTranslations("share")
  const session = useTranslations("session")
  const router = useRouter()
  const { user, loading } = useAuth()
  const [invite, setInvite] = useState<Invite | null>(null)
  const [missing, setMissing] = useState(false)
  const [starting, setStarting] = useState(false)

  useEffect(() => {
    if (user) {
      apiFetch<Invite>(`/companies/invites/${token}`)
        .then(setInvite)
        .catch(() => setMissing(true))
    }
  }, [user, token])

  async function start() {
    setStarting(true)

    try {
      const result = await apiFetch<{ sessions: SessionSummary[] }>(
        `/companies/invites/${token}/start`,
        { method: "POST" }
      )

      const next =
        result.sessions.find((item) => item.status !== "finished") ??
        result.sessions[0]

      if (next) {
        router.push(`/sessions/${next.id}`)

        return
      }

      setStarting(false)
    } catch (error) {
      const forbidden = error instanceof ApiError && error.status === 403
      // The API's own message, such as the pause's, before the generic one.
      toast.error(
        forbidden
          ? share("wrongEmail")
          : apiErrorMessage(error, session("startFailed"))
      )
      setStarting(false)
    }
  }

  if (!loading && !user) {
    return <SignInPrompt message={t("signIn")} />
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
    <InviteIntro
      company={invite.company}
      logoUrl={invite.logo_url}
      verifiedDomain={invite.verified_domain}
      title={invite.title}
      questionSeconds={invite.question_seconds}
      finished={invite.status === "finished"}
      action={
        matches ? (
          <Button
            className="h-12 px-6 text-base"
            disabled={starting}
            onClick={start}
          >
            {invite.status === "in_process" ? t("continue") : t("start")}
          </Button>
        ) : (
          <p className="text-base text-muted-foreground">{t("mismatch")}</p>
        )
      }
    />
  )
}
