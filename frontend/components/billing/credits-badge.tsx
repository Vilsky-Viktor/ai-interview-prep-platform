"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useLocale, useTranslations } from "next-intl"
import { useEffect, useState } from "react"

import { useAuth } from "@/components/auth-provider"
import { apiFetch } from "@/lib/api"
import { onCreditsChanged } from "@/lib/credits"
import { cn } from "cn"
import type { Balance } from "@/types/billing"

/** The signed-in user's available credits, next to their avatar; a link to top up. */
export function CreditsBadge() {
  const t = useTranslations("billing")
  const locale = useLocale()
  const { user } = useAuth()
  const pathname = usePathname()
  const [balance, setBalance] = useState<Balance | null>(null)

  useEffect(() => {
    if (!user) {
      return
    }

    const load = () =>
      apiFetch<Balance>("/billing/me")
        .then(setBalance)
        .catch(() => {})

    // Spending happens on other pages, so it reloads on each page and after a payment.
    void load()

    return onCreditsChanged(load)
  }, [user, pathname])

  if (!user || balance === null) {
    return null
  }

  const { available, low } = balance

  return (
    <Link
      href="/top-up"
      aria-label={t(low ? "balanceLow" : "balance", { count: available })}
      className={cn(
        "flex h-8 items-center rounded-full px-4 transition-colors",
        low
          ? "bg-amber-500/10 text-amber-600 hover:bg-amber-500/20 dark:text-amber-400"
          : "bg-muted/60 hover:bg-muted"
      )}
    >
      {/* The pill centres the group; inside it, the number and the word share a baseline. */}
      <span className="flex items-baseline gap-1 leading-none">
        <span className="font-heading text-sm font-medium tabular-nums">
          {available.toLocaleString(locale)}
        </span>
        <span className={cn("text-xs", !low && "text-muted-foreground")}>
          {t("creditsWord", { count: available })}
        </span>
      </span>
    </Link>
  )
}
