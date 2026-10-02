"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/components/auth-provider"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { Button } from "@/components/ui/button"
import { ApiError, apiFetch } from "@/lib/api"
import type { InviteView as Invite, SessionSummary } from "@/types/company"

export function InviteView({ token }: { token: string }) {
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
      toast.error(
        forbidden
          ? "This invite was sent to a different email address."
          : "Couldn't start the interview. Please try again."
      )
      setStarting(false)
    }
  }

  if (!loading && !user) {
    return (
      <SignInPrompt message="Sign in with the invitation email to take this interview." />
    )
  }

  if (missing) {
    return (
      <p className="py-24 text-center text-base text-muted-foreground">
        This invite isn&apos;t valid anymore.
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
            <span className="font-medium text-foreground">
              {invite.company}
            </span>{" "}
            invited you to interview.
          </p>
        )}
        <h1 className="font-heading text-4xl font-medium tracking-tight text-balance sm:text-5xl">
          {invite.title ?? "an interview"}
        </h1>
        {invite.question_seconds != null && invite.status !== "finished" && (
          <p className="pt-6 text-base text-muted-foreground">
            Time per question:
            <span className="block">
              <span className="text-3xl font-medium text-foreground tabular-nums">
                {invite.question_seconds}
              </span>{" "}
              s
            </span>
          </p>
        )}
      </div>
      {invite.status !== "finished" && (
        <ul className="mx-auto max-w-lg list-disc space-y-2 pl-5 text-left text-base text-muted-foreground">
          <li>Pick one of four options for each question.</li>
          <li>An answer can&apos;t be changed once given.</li>
          {invite.question_seconds != null && (
            <li>
              When a question&apos;s time runs out, it counts as wrong and the
              next one opens. The clock keeps running if you leave.
            </li>
          )}
          <li>Unanswered questions count as wrong.</li>
          <li>Progress is saved: use this link again to continue.</li>
          <li>
            Stay on this page: leaving it or copying is recorded (
            <Link href="/privacy" className="underline underline-offset-4">
              how we handle it
            </Link>
            ).
          </li>
          {invite.share_results && (
            <li>You&apos;ll see whether each answer was right.</li>
          )}
        </ul>
      )}
      {invite.status === "finished" ? (
        <p className="text-base text-muted-foreground">
          This interview is already finished.
        </p>
      ) : matches ? (
        <Button
          className="h-12 px-6 text-base"
          disabled={starting}
          onClick={start}
        >
          {invite.status === "in_process" ? "Continue" : "Accept & Start"}
        </Button>
      ) : (
        <p className="text-base text-muted-foreground">
          The email does not match. Sign in with the invitation email to start.
        </p>
      )}
    </div>
  )
}
