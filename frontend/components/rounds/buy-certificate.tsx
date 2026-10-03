"use client"

import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { apiErrorMessage, apiFetch } from "@/lib/api"
import { topUpAction } from "@/lib/credits"
import type { Certificate } from "@/types/round"

/** An earned certificate on someone else's public kit: charged and issued in one step. */
export function BuyCertificate({
  topicId,
  price,
}: {
  topicId: string
  price: number
}) {
  const t = useTranslations("rounds")
  const common = useTranslations("common")
  const billing = useTranslations("billing")
  const router = useRouter()
  const [buying, setBuying] = useState(false)

  async function buy() {
    setBuying(true)

    try {
      const certificate = await apiFetch<Certificate>(
        `/rounds/certificates/topics/${topicId}`,
        { method: "POST" }
      )
      router.push(`/certificates/${certificate.id}`)
    } catch (error) {
      toast.error(
        apiErrorMessage(error, common("failed")),
        topUpAction(error, billing("topUp"), () => router.push("/top-up"))
      )
      setBuying(false)
    }
  }

  return (
    <Button disabled={buying} onClick={buy}>
      {t("buyCertificate", { count: price })}
    </Button>
  )
}
