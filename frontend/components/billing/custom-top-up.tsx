"use client"

import { useTranslations } from "next-intl"
import { useEffect, useState } from "react"

import { BuyButton } from "@/components/billing/buy-button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { apiFetch } from "@/lib/api"
import type { Catalog, Quote } from "@/types/billing"

/** Any whole-dollar amount in billing's range; billing quotes what it buys. */
export function CustomTopUp({
  catalog,
  companyId,
}: {
  catalog: Catalog
  companyId?: string
}) {
  const t = useTranslations("billing")
  const {
    min_dollars: min,
    max_dollars: max,
    price_id: priceId,
  } = catalog.custom
  const [dollars, setDollars] = useState("")
  const [quote, setQuote] = useState<Quote | null>(null)
  const amount = Number(dollars)

  // An amount out of range gets no quote, which keeps the button off.
  useEffect(() => {
    if (!dollars) {
      return
    }

    const timer = window.setTimeout(() => {
      apiFetch<Quote>(
        `/billing/topups/quote?dollars=${encodeURIComponent(dollars)}`
      )
        .then(setQuote)
        .catch(() => {})
    }, 300)

    return () => window.clearTimeout(timer)
  }, [dollars])

  // Digits only, never over the maximum while typing; below the minimum is lifted to it on
  // leaving the field, since "2" is on its way to "20".
  function change(value: string) {
    const digits = value.replace(/\D/g, "")
    const next = digits && Number(digits) > max ? String(max) : digits

    setDollars(next)
    setQuote(null)
  }

  function lift() {
    if (dollars && Number(dollars) < min) {
      change(String(min))
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-4 rounded-2xl border p-5">
      <p className="font-medium">{t("customAmount")}</p>
      <div className="relative w-28 rounded-full border border-transparent transition-colors focus-within:border-ring">
        <span className="pointer-events-none absolute start-4 top-1/2 -translate-y-1/2 text-lg text-muted-foreground">
          $
        </span>
        <Input
          type="text"
          inputMode="numeric"
          value={dollars}
          placeholder="20"
          aria-label={t("customAmount")}
          className="h-10 border-0 ps-8 text-lg tabular-nums focus-visible:ring-0 md:text-lg"
          onChange={(event) => change(event.target.value)}
          onBlur={lift}
        />
      </div>
      {quote && (
        <span className="flex items-center gap-2 text-sm text-muted-foreground tabular-nums">
          {t("credits", { count: quote.credits })}
          {quote.bonus_credits > 0 && (
            <Badge className="font-light">
              {t("bonus", { count: quote.bonus_credits })}
            </Badge>
          )}
        </span>
      )}
      <BuyButton
        catalog={catalog}
        priceId={priceId}
        quantity={amount}
        companyId={companyId}
        disabled={!quote}
        className="ms-auto h-10 px-5"
      />
    </div>
  )
}
