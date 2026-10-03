"use client"

import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/components/auth-provider"
import { Button } from "@/components/ui/button"
import { apiFetch } from "@/lib/api"
import { signIn } from "@/lib/auth"
import type { PreparationSummary } from "@/types/preparation"

export function MembershipButton({
  preparation,
  joined,
}: {
  preparation: PreparationSummary
  joined: boolean
}) {
  const t = useTranslations("membership")
  const common = useTranslations("common")
  const signInText = useTranslations("signIn")
  const router = useRouter()
  const { user } = useAuth()
  const [busy, setBusy] = useState(false)

  async function toggle() {
    setBusy(true)

    try {
      await apiFetch(`/library/preparations/${preparation.id}/join`, {
        method: joined ? "DELETE" : "POST",
      })

      if (joined && preparation.visibility === "private") {
        // A shared private preparation is gone for this user after leaving.
        router.push("/preparations")

        return
      }

      router.refresh()
    } catch {
      toast.error(common("failed"))
    } finally {
      setBusy(false)
    }
  }

  if (!user) {
    return (
      <Button onClick={() => signIn(signInText("failed"))}>
        {t("signIn")}
      </Button>
    )
  }

  return (
    <Button
      variant={joined ? "outline" : "default"}
      disabled={busy}
      onClick={toggle}
    >
      {joined ? t("leave") : t("join")}
    </Button>
  )
}
