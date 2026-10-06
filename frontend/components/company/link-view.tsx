"use client"

import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useEffect, useState } from "react"
import { toast } from "sonner"

import { useSignIn } from "@/components/sign-in-dialog"
import { useAuth } from "@/components/auth-provider"
import { InviteIntro } from "@/components/company/invite-intro"
import { Button } from "@/components/ui/button"
import { ApiError, apiErrorMessage, apiFetch } from "@/lib/api"
import type { JobLink, SessionSummary } from "@/types/company"

/** What someone sees from a test's shareable link: the same intro as an invite; starting signs
 * them in with Google first, which gives their name and verified email. */
export function LinkView({ token }: { token: string }) {
  const t = useTranslations("invite")
  const share = useTranslations("share")
  const session = useTranslations("session")
  const signIn = useSignIn()
  const router = useRouter()
  const { user, loading } = useAuth()
  const [link, setLink] = useState<JobLink | null>(null)
  const [missing, setMissing] = useState(false)
  const [starting, setStarting] = useState(false)

  // Once sign-in is known, and again after signing in, so a finished test is never offered.
  useEffect(() => {
    if (!loading) {
      apiFetch<JobLink>(`/companies/links/${token}`)
        .then(setLink)
        .catch(() => setMissing(true))
    }
  }, [token, loading, user])

  async function start() {
    setStarting(true)

    if (!user && !(await signIn())) {
      setStarting(false)

      return
    }

    try {
      const result = await apiFetch<{ sessions: SessionSummary[] }>(
        `/companies/links/${token}/start`,
        { method: "POST" }
      )
      const next =
        result.sessions.find((item) => item.status !== "finished") ??
        result.sessions[0]

      if (next) {
        router.push(`/sessions/${next.id}`)

        return
      }
    } catch (error) {
      // Already finished, or the company has stopped taking candidates: the API says which.
      const refused = error instanceof ApiError && error.status === 409
      toast.error(
        refused ? error.message : apiErrorMessage(error, session("startFailed"))
      )
    }

    setStarting(false)
  }

  if (missing) {
    return (
      <p className="py-24 text-center text-base text-muted-foreground">
        {share("invalid")}
      </p>
    )
  }

  if (!link) {
    return null
  }

  return (
    <InviteIntro
      company={link.company}
      logoUrl={link.logo_url}
      verifiedDomain={link.verified_domain}
      title={link.title}
      questionSeconds={link.question_seconds}
      finished={link.status === "finished"}
      action={
        <Button
          className="h-12 px-6 text-base"
          disabled={starting}
          onClick={start}
        >
          {link.status === "in_process" ? t("continue") : t("start")}
        </Button>
      }
    />
  )
}
