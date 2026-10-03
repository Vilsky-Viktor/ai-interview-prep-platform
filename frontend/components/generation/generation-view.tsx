"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useEffect, useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/components/auth-provider"
import { BackLink } from "@/components/back-link"
import { CancelGeneration } from "@/components/generation/cancel-generation"
import { GenerationProgress } from "@/components/generation/generation-progress"
import { TopicReview } from "@/components/generation/topic-review"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { Button } from "@/components/ui/button"
import { ACTIVE_STATUSES, POLL_INTERVAL_MS } from "@/constants/generation"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import { topUpAction } from "@/lib/credits"
import type { DraftTopic, Generation } from "@/types/generation"

export function GenerationView({
  path,
  next,
  backHref,
  backLabel,
}: {
  path: string
  next?: string
  backHref: string
  backLabel: string
}) {
  const t = useTranslations("generation")
  const billing = useTranslations("billing")
  const { user, loading } = useAuth()
  const router = useRouter()
  const [generation, setGeneration] = useState<Generation | null>(null)
  const [missing, setMissing] = useState(false)
  // Bumped after a review so polling starts again.
  const [round, setRound] = useState(0)

  useEffect(() => {
    if (!user) {
      return
    }

    let active = true
    let timer: ReturnType<typeof setTimeout> | undefined

    async function load() {
      try {
        const next = await apiFetch<Generation>(path)

        if (!active) {
          return
        }

        setGeneration(next)

        if (ACTIVE_STATUSES.includes(next.status)) {
          timer = setTimeout(load, POLL_INTERVAL_MS)
        }
      } catch {
        if (active) {
          setMissing(true)
        }
      }
    }

    load()

    return () => {
      active = false
      clearTimeout(timer)
    }
  }, [user, path, round])

  useEffect(() => {
    if (generation?.status === "done") {
      router.replace(next ?? `/preparations/${generation.preparation_id}`)
    }
  }, [generation, next, router])

  async function submitReview(
    selected: number[],
    instructions: string,
    topics: DraftTopic[] | null
  ) {
    try {
      const next = await apiFetch<Generation>(`${path}/review`, {
        method: "POST",
        body: JSON.stringify({ selected, instructions, topics }),
      })
      setGeneration(next)
      setRound((value) => value + 1)
    } catch {
      toast.error(t("reviewFailed"))
    }
  }

  async function retry() {
    try {
      const next = await apiFetch<Generation>(`${path}/retry`, {
        method: "POST",
      })
      setGeneration(next)
      setRound((value) => value + 1)
    } catch (error) {
      toast.error(
        apiErrorMessage(error, t("retryFailed")),
        topUpAction(error, billing("topUp"), () => router.push("/top-up"))
      )
    }
  }

  if (!loading && !user) {
    return (
      <WithBack href={backHref} label={backLabel}>
        <SignInPrompt message={t("signIn")} />
      </WithBack>
    )
  }

  if (missing) {
    return (
      <WithBack href={backHref} label={backLabel}>
        <Message text={t("missing")} />
      </WithBack>
    )
  }

  if (generation?.status === "cancelled") {
    return (
      <WithBack href={backHref} label={backLabel}>
        <Message text={t("cancelled")} />
      </WithBack>
    )
  }

  const cancel = <CancelGeneration path={path} leaveTo={backHref} />

  if (generation?.status === "failed") {
    return (
      <WithBack href={backHref} label={backLabel}>
        <Message text={t("failed")} onRetry={retry} />
        {cancel && <div className="flex justify-center">{cancel}</div>}
      </WithBack>
    )
  }

  if (generation?.status === "awaiting_review" && generation.topics) {
    return (
      <TopicReview
        key={round}
        topics={generation.topics}
        maxTopics={generation.max_topics}
        back={<BackLink href={backHref}>{backLabel}</BackLink>}
        cancel={cancel}
        onSubmit={submitReview}
      />
    )
  }

  if (!generation || generation.status === "done") {
    return null
  }

  return (
    <GenerationProgress
      generation={generation}
      backHref={backHref}
      backLabel={backLabel}
      action={cancel}
    />
  )
}

function WithBack({
  href,
  label,
  children,
}: {
  href: string
  label: string
  children: React.ReactNode
}) {
  return (
    <div className="relative">
      <BackLink href={href}>{label}</BackLink>
      {children}
    </div>
  )
}

function Message({
  text,
  onRetry,
}: {
  text: string
  onRetry?: () => Promise<void>
}) {
  const t = useTranslations("generation")
  const [retrying, setRetrying] = useState(false)

  async function retry() {
    setRetrying(true)
    await onRetry?.()
    setRetrying(false)
  }

  return (
    <div className="flex flex-col items-center gap-8 py-24 text-center">
      <p className="text-base text-muted-foreground">{text}</p>
      <div className="flex flex-wrap justify-center gap-3">
        {onRetry && (
          <Button
            className="h-12 px-6 text-base"
            disabled={retrying}
            onClick={retry}
          >
            {retrying ? t("retrying") : t("retry")}
          </Button>
        )}
        <Button
          variant="outline"
          className="h-12 px-6 text-base"
          render={<Link href="/" />}
          nativeButton={false}
        >
          {t("startOver")}
        </Button>
      </div>
    </div>
  )
}
