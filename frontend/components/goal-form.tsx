"use client"

import { ArrowUpIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/components/auth-provider"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import { signIn } from "@/lib/auth"
import { topUpAction } from "@/lib/credits"
import { isSubmitShortcut } from "@/lib/keys"
import type { Generation } from "@/types/generation"

export function GoalForm() {
  const t = useTranslations("goal")
  const common = useTranslations("common")
  const signInText = useTranslations("signIn")
  const { user } = useAuth()
  const router = useRouter()
  const [goal, setGoal] = useState("")
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!user) {
      await signIn(signInText("failed"))

      return
    }

    setSubmitting(true)

    try {
      const generation = await apiFetch<Generation>("/generate/generations", {
        method: "POST",
        body: JSON.stringify({ text: goal.trim() }),
      })
      router.push(`/generate/${generation.id}`)
    } catch (error) {
      toast.error(
        apiErrorMessage(error, t("failed")),
        topUpAction(error, t("seePlans"), () => router.push("/top-up"))
      )
      setSubmitting(false)
    }
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (isSubmitShortcut(event)) {
      event.preventDefault()
      event.currentTarget.form?.requestSubmit()
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="w-full rounded-2xl border border-transparent bg-card p-3 transition-colors focus-within:border-ring"
    >
      <Textarea
        value={goal}
        onChange={(event) => setGoal(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={t("placeholder")}
        aria-label={t("label")}
        className="max-h-72 min-h-40 resize-none border-0 bg-transparent p-2 text-base shadow-none focus-visible:ring-0 md:text-base dark:bg-transparent"
      />
      <div className="flex items-center justify-between gap-4 pt-2 pl-2">
        <p className="text-xs text-muted-foreground">{common("submitHint")}</p>
        <Button
          type="submit"
          size="icon-lg"
          className="rounded-full"
          disabled={!goal.trim() || submitting}
          aria-label={t("submit")}
        >
          <ArrowUpIcon />
        </Button>
      </div>
    </form>
  )
}
