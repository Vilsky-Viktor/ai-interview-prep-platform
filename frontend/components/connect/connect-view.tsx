"use client"

import { useTranslations } from "next-intl"
import { useEffect, useState } from "react"

import { useAuth } from "@/components/auth-provider"
import { ConsentCard } from "@/components/connect/consent-card"
import { useSignIn } from "@/components/sign-in-dialog"
import { Button } from "@/components/ui/button"
import { InfoCard } from "@/components/warning-card"
import { ApiError, apiFetch } from "@/lib/api"
import type { ConnectRequest } from "@/types/connections"

/** The consent page's states: an expired or used request; signed out, which app asks (when the
 * API says so before sign-in) and Sign in; signed in, the consent card. */
export function ConnectView({ requestId }: { requestId: string }) {
  const t = useTranslations("connect")
  const { user, loading } = useAuth()
  const signIn = useSignIn()
  const [request, setRequest] = useState<ConnectRequest | null>(null)
  const [expired, setExpired] = useState(!requestId)
  const [read, setRead] = useState(false)

  // Read signed in or not; again after signing in, so the card appears in place.
  useEffect(() => {
    if (loading || !requestId) {
      return
    }

    apiFetch<ConnectRequest>(
      `/assistant/connect/${encodeURIComponent(requestId)}`
    )
      .then(setRequest)
      .catch((error) => {
        if (error instanceof ApiError && error.status === 404) {
          setExpired(true)
        }
      })
      .finally(() => setRead(true))
  }, [loading, user, requestId])

  if (expired) {
    return <InfoCard className="w-full max-w-md">{t("expired")}</InfoCard>
  }

  if (!read) {
    return null
  }

  if (!user) {
    return (
      <div className="w-full max-w-md space-y-6 rounded-2xl border p-6 sm:p-8">
        <div className="space-y-3">
          <h1 className="font-heading text-3xl font-medium tracking-tight text-balance">
            {request
              ? t.rich("title", {
                  client: request.client_name,
                  name: (chunks) => (
                    <span className="normal-case">{chunks}</span>
                  ),
                })
              : t("titleAny")}
          </h1>
          <p className="text-base text-muted-foreground">{t("signInText")}</p>
        </div>
        <Button className="h-12 w-full px-6 text-base" onClick={() => signIn()}>
          {t("signIn")}
        </Button>
      </div>
    )
  }

  if (!request) {
    return (
      <p className="py-24 text-center text-base text-muted-foreground">
        {t("loadFailed")}
      </p>
    )
  }

  return (
    <ConsentCard
      requestId={requestId}
      request={request}
      email={user.email ?? ""}
    />
  )
}
