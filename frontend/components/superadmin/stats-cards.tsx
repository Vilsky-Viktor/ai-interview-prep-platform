import { useFormatter, useLocale, useTranslations } from "next-intl"

import { STATS_CARDS, STATS_SOURCES } from "@/constants/stats"
import { formatPrice } from "@/lib/format"
import type { Stats } from "@/types/superadmin"

type Source = (typeof STATS_SOURCES)[number]

/** The numbers as cards, three to a row and centred, like the pricing cards; a dash where the
 * service didn't answer. */
export function StatsCards({ stats }: { stats: Record<Source, Stats | null> }) {
  const t = useTranslations("superadmin")
  const format = useFormatter()
  const locale = useLocale()

  function value(card: (typeof STATS_CARDS)[number]) {
    const source = stats[card.source]
    const amount = source?.counts[card.metric]

    if (amount === undefined) {
      return "—"
    }

    if (card.metric === "paid" && source?.currency) {
      return formatPrice(amount, source.currency, locale)
    }

    return format.number(amount)
  }

  return (
    <dl className="flex flex-wrap justify-center gap-4">
      {STATS_CARDS.map((card) => (
        <div
          key={card.metric}
          className="flex w-full flex-col-reverse gap-1 rounded-2xl border p-6 text-center sm:w-[calc((100%-1rem)/2)] lg:w-[calc((100%-2rem)/3)]"
        >
          <dt className="text-sm text-muted-foreground">
            {t(`statsCards.${card.metric}`)}
          </dt>
          <dd className="font-heading text-5xl font-medium tracking-tight text-primary tabular-nums">
            {value(card)}
          </dd>
        </div>
      ))}
    </dl>
  )
}
