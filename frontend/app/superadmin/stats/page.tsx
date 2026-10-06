import { notFound } from "next/navigation"

import { StatsCards } from "@/components/superadmin/stats-cards"
import { StatsPicker } from "@/components/superadmin/stats-picker"
import { SuperadminHeader } from "@/components/superadmin/superadmin-header"
import { ALL_TIME, MONTH_PATTERN, STATS_SOURCES } from "@/constants/stats"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"
import type { Stats } from "@/types/superadmin"

export const generateMetadata = () => translatedTitle("superadmin", "zone")

/** The admin zone's stats for one month (`?month=2026-10`, this UTC month by default) or all
 * time (`&all=1`, the month kept for turning it off), from each service. The API answers
 * superadmins only; a service that doesn't answer leaves its cards with a dash. */
export default async function StatsPage({
  searchParams,
}: {
  searchParams: Promise<{ month?: string; all?: string }>
}) {
  const { month: asked, all } = await searchParams
  const allTime = all === ALL_TIME
  const month =
    asked && MONTH_PATTERN.test(asked)
      ? asked
      : new Date().toISOString().slice(0, 7)
  const query = allTime ? "" : `?month=${month}`
  const [companies, rounds, billing] = await Promise.all(
    STATS_SOURCES.map((source) =>
      serverFetch<Stats>(`/${source}/superadmin/stats${query}`).catch(
        () => null
      )
    )
  )

  if (!companies) {
    notFound()
  }

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <SuperadminHeader current="stats" />
      <div className="space-y-4">
        <StatsPicker month={month} allTime={allTime} />
        <StatsCards stats={{ companies, rounds, billing }} />
      </div>
    </main>
  )
}
