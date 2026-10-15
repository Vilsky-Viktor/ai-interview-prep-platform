"use client"

import { useRouter, useSearchParams } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/components/auth-provider"
import { InviteIntro } from "@/components/company/invite-intro"
import { LinkStatus } from "@/components/link-status"
import { useSignIn } from "@/components/sign-in-dialog"
import { Button } from "@/components/ui/button"
import { WarningCard } from "@/components/warning-card"
import { ApiError, apiErrorMessage, apiFetch } from "@/lib/api"
import { refreshVerification, signInAsGuest } from "@/lib/auth"
import { useBrandColors } from "@/hooks/use-brand-colors"
import { useLinkData } from "@/hooks/use-link-data"
import type { InviteView as Invite, SessionSummary } from "@/types/company"

/** The invitation. Embedded in a company's site, `onStarted` opens the interview in place
 * instead of going to its page. */
export function InviteView({
  token,
  onStarted,
}: {
  token: string
  onStarted?: (sessionId: string) => void
}) {
  const t = useTranslations("invite")
  const share = useTranslations("share")
  const session = useTranslations("session")
  const router = useRouter()
  const { user, loading } = useAuth()
  const signIn = useSignIn()
  const [starting, setStarting] = useState(false)
  // Read signed in or not, so a visitor sees what the invitation is for before signing in;
  // again after signing in, for whose it is.
  const {
    data: invite,
    status,
    retry,
    gone,
  } = useLinkData<Invite>(
    loading ? null : `/companies/invites/${token}`,
    user?.uid
  )

  useBrandColors(invite?.brand_colors, invite?.theme, invite?.brand_style)
  // A theme the address asks for goes on with the candidate to the questions.
  const asked = useSearchParams().get("theme")

  async function start() {
    setStarting(true)

    try {
      // Sent by the company's own platform: the link signs the candidate in.
      if (invite?.guest) {
        const guest = await apiFetch<{ token: string }>(
          `/companies/invites/${token}/guest`,
          { method: "POST" }
        )
        await signInAsGuest(guest.token)
      } else {
        await refreshVerification()
      }

      const result = await apiFetch<{ sessions: SessionSummary[] }>(
        `/companies/invites/${token}/start`,
        { method: "POST" }
      )

      const next =
        result.sessions.find((item) => item.status !== "finished") ??
        result.sessions[0]

      if (next && onStarted) {
        onStarted(next.id)

        return
      }

      if (next) {
        router.push(
          `/sessions/${next.id}${asked ? `?theme=${encodeURIComponent(asked)}` : ""}`
        )

        return
      }

      setStarting(false)
    } catch (error) {
      // Another email, or theirs not confirmed yet, or the pause: the API says which.
      const refused =
        error instanceof ApiError && [403, 409].includes(error.status)
      toast.error(
        refused ? error.message : apiErrorMessage(error, session("startFailed"))
      )
      setStarting(false)
    }
  }

  if (status !== "ready" || !invite) {
    return (
      <LinkStatus
        status={status === "ready" ? "loading" : status}
        invalid={gone ?? share("invalid")}
        onRetry={retry}
      />
    )
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
        // A guest's link is all they need; anyone else signs in with the invited email.
        !invite.guest && !user ? (
          <Button className="h-12 px-6 text-base" onClick={() => signIn()}>
            {t("signInToStart")}
          </Button>
        ) : invite.guest || matches ? (
          <Button
            className="h-12 px-6 text-base"
            disabled={starting}
            onClick={start}
          >
            {invite.status === "in_process" ? t("continue") : t("start")}
          </Button>
        ) : (
          // Signed in with another email: a warning, in the warning card.
          <WarningCard className="text-start">{t("mismatch")}</WarningCard>
        )
      }
    />
  )
}
