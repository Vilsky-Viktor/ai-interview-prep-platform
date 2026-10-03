"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useLocale, useTranslations } from "next-intl"
import { useEffect, useState } from "react"

import { useAuth } from "@/components/auth-provider"
import { apiFetch } from "@/lib/api"
import { onCreditsChanged } from "@/lib/credits"
import type { Balance } from "@/types/billing"

/** The signed-in user's available credits, next to their avatar; a link to top up. */
export function CreditsBadge() {
  const t = useTranslations("billing")
  const locale = useLocale()
  const { user } = useAuth()
  const pathname = usePathname()
  const [available, setAvailable] = useState<number | null>(null)

  useEffect(() => {
    if (!user) {
      return
    }

    const load = () =>
      apiFetch<Balance>("/billing/me")
        .then((balance) => setAvailable(balance.available))
        .catch(() => {})

    // Spending happens on other pages, so it reloads on each page and after a payment.
    void load()

    return onCreditsChanged(load)
  }, [user, pathname])

  if (!user || available === null) {
    return null
  }

  return (
    <Link
      href="/top-up"
      aria-label={t("balance", { count: available })}
      className="flex h-8 items-center rounded-full bg-muted/60 px-4 transition-colors hover:bg-muted"
    >
      {/* The pill centres the group; inside it, the number and the word share a baseline. */}
      <span className="flex items-baseline gap-1 leading-none">
        <span className="font-heading text-sm font-medium tabular-nums">
          {available.toLocaleString(locale)}
        </span>
        <span className="text-xs text-muted-foreground">
          {t("creditsWord", { count: available })}
        </span>
      </span>
    </Link>
  )
}
