"use client"

import { useFormatter, useTranslations } from "next-intl"
import { usePathname, useRouter } from "next/navigation"

import { PillSelect } from "@/components/pill-select"
import { Button } from "@/components/ui/button"
import { ALL_TIME, STATS_MONTHS } from "@/constants/stats"

/** All time, or one of the last twelve UTC months in the site's select; the choice lives in the
 * address (`?month=2026-10`, with `&all=1` for all time), so the server renders it. "All time"
 * turns off again to the month picked before; picking a month turns it off. */
export function StatsPicker({
  month,
  allTime,
}: {
  month: string
  allTime: boolean
}) {
  const t = useTranslations("superadmin")
  const format = useFormatter()
  const router = useRouter()
  const pathname = usePathname()
  const now = new Date()
  const months = Array.from({ length: STATS_MONTHS }, (_, index) => {
    const start = new Date(
      Date.UTC(now.getUTCFullYear(), now.getUTCMonth() - index, 15)
    )

    return {
      value: start.toISOString().slice(0, 7),
      label: format.dateTime(start, {
        month: "long",
        year: "numeric",
        timeZone: "UTC",
      }),
    }
  })

  return (
    <div className="flex flex-wrap items-center justify-end gap-3">
      <Button
        variant={allTime ? "default" : "outline"}
        aria-pressed={allTime}
        onClick={() =>
          router.replace(
            `${pathname}?month=${month}${allTime ? "" : `&all=${ALL_TIME}`}`,
            { scroll: false }
          )
        }
        className="h-12 shrink-0 px-6 text-base"
      >
        {t("statsAllTime")}
      </Button>
      <PillSelect
        ariaLabel={t("statsMonth")}
        value={month}
        className="w-60"
        options={months}
        onChange={(value) =>
          router.replace(`${pathname}?month=${value}`, { scroll: false })
        }
      />
    </div>
  )
}
