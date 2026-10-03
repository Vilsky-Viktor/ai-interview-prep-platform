"use client"

import { cn } from "cn"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { useState } from "react"
import { toast } from "sonner"

import { useAuth } from "@/components/auth-provider"
import { Button } from "@/components/ui/button"
import { signIn } from "@/lib/auth"
import { announceCreditsChanged } from "@/lib/credits"
import { openCheckout } from "@/lib/paddle"
import type { Catalog } from "@/types/billing"

/** Buys a top-up for the signed-in user, or for `companyId` when given: Paddle's `priceId`,
`quantity` times. */
export function BuyButton({
  catalog,
  priceId,
  quantity = 1,
  disabled = false,
  companyId,
  label,
  variant = "default",
  className,
}: {
  catalog: Catalog
  // None while the price isn't on sale yet.
  priceId: string | null
  quantity?: number
  // A custom amount not quoted yet, or out of range.
  disabled?: boolean
  companyId?: string
  label?: string
  variant?: "default" | "outline"
  className?: string
}) {
  const t = useTranslations("billing")
  const signInText = useTranslations("signIn")
  const router = useRouter()
  const { user } = useAuth()
  const [opening, setOpening] = useState(false)

  if (!priceId) {
    return (
      <Button
        variant="outline"
        className={cn("h-12 px-6 text-base", className)}
        disabled
      >
        {label ?? t("topUp")}
      </Button>
    )
  }

  async function buy() {
    if (!user) {
      await signIn(signInText("failed"))

      return
    }

    setOpening(true)

    try {
      await openCheckout(
        catalog,
        priceId!,
        companyId
          ? { owner_type: "company", owner_id: companyId, buyer_id: user.uid }
          : { owner_type: "user", owner_id: user.uid, buyer_id: user.uid },
        user.email,
        () => {
          toast.success(t("paid"))
          // The webhook usually lands within seconds; show the new balance then.
          window.setTimeout(() => {
            router.refresh()
            announceCreditsChanged()
          }, 4000)
        },
        quantity
      )
    } catch {
      toast.error(t("checkoutFailed"))
    } finally {
      setOpening(false)
    }
  }

  return (
    <Button
      variant={variant}
      className={cn("h-12 px-6 text-base", className)}
      disabled={opening || disabled}
      onClick={buy}
    >
      {label ?? t("topUp")}
    </Button>
  )
}
