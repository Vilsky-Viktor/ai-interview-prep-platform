"use client"

import { cn } from "cn"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useEffect, useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/components/auth-provider"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { Button } from "@/components/ui/button"
import { ApiError, apiFetch } from "@/lib/api"
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
      toast.error(forbidden ? share("wrongEmail") : session("startFailed"))
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
    <div className="w-full space-y-8 text-center">
      <div className="space-y-4">
        {invite.company && (
          <p className="text-base text-muted-foreground">
            {t.rich("invitedYou", {
              company: invite.company,
              b: (chunks) => (
                <span className="font-medium text-foreground">{chunks}</span>
              ),
            })}
          </p>
        )}
        <h1
          className={cn(
            "font-heading text-4xl font-medium tracking-tight text-balance sm:text-5xl",
            invite.title && "normal-case"
          )}
        >
          {invite.title ?? t("fallbackTitle")}
        </h1>
        {invite.status !== "finished" && (
          <p className="pt-6 text-base text-muted-foreground">
            {t("timePerQuestion")}
            <span className="block">
              <span className="text-3xl font-medium text-foreground tabular-nums">
                {invite.question_seconds}
              </span>{" "}
              {t("secondsUnit")}
            </span>
          </p>
        )}
      </div>
      {invite.status !== "finished" && (
        <ul className="mx-auto max-w-lg list-disc space-y-2 ps-5 text-start text-base text-muted-foreground">
          <li>{t("pickOne")}</li>
          <li>{t("noChange")}</li>
          <li>{t("timeRunsOut")}</li>
          <li>{t("unanswered")}</li>
          <li>{t("saved")}</li>
          <li>
            {t.rich("stay", {
              link: (chunks) => (
                <Link href="/privacy" className="underline underline-offset-4">
                  {chunks}
                </Link>
              ),
            })}
          </li>
        </ul>
      )}
      {invite.status === "finished" ? (
        <p className="text-base text-muted-foreground">{t("finished")}</p>
      ) : matches ? (
        <Button
          className="h-12 px-6 text-base"
          disabled={starting}
          onClick={start}
        >
          {invite.status === "in_process" ? t("continue") : t("start")}
        </Button>
      ) : (
        <p className="text-base text-muted-foreground">{t("mismatch")}</p>
      )}
    </div>
  )
}
