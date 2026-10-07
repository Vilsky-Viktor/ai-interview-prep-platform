"use client"

import { useEffect, useState, useSyncExternalStore } from "react"

import { StatsCards } from "@/components/superadmin/stats-cards"
import { StatsPicker } from "@/components/superadmin/stats-picker"
import { STATS_SOURCES } from "@/constants/stats"
import { apiFetch } from "@/lib/api"
import {
  parseStatsChoice,
  savedStatsChoice,
  writeStatsChoice,
  type StatsChoice,
} from "@/lib/stats-period"
import type { Stats } from "@/types/superadmin"

type Source = (typeof STATS_SOURCES)[number]

// Storage isn't watched for changes from other tabs: the choice is read once per visit.
const unwatched = () => () => {}

/** The stats tab: the choice the browser kept from last time (this month at first), and each
 * service's numbers for it, asked again whenever the choice changes. A service that doesn't
 * answer leaves its cards with a dash. */
export function StatsView() {
  // The saved choice exists only in the browser: the server renders without it (null).
  const saved = useSyncExternalStore(unwatched, savedStatsChoice, () => null)
  const [picked, setPicked] = useState<StatsChoice | null>(null)
  const [stats, setStats] = useState<Record<Source, Stats | null> | null>(null)
  const choice =
    picked ?? (saved === null ? null : parseStatsChoice(saved, new Date()))
  const query = !choice
    ? null
    : choice.allTime
      ? ""
      : `?period=${choice.period}`

  useEffect(() => {
    if (query === null) {
      return
    }

    let current = true

    Promise.all(
      STATS_SOURCES.map((source) =>
        apiFetch<Stats>(`/${source}/superadmin/stats${query}`).catch(() => null)
      )
    ).then(([companies, rounds, billing]) => {
      if (current) {
        setStats({ companies, rounds, billing })
      }
    })

    return () => {
      current = false
    }
  }, [query])

  function change(next: StatsChoice) {
    setPicked(next)
    writeStatsChoice(next)
  }

  return (
    <div className="space-y-4">
      {choice && <StatsPicker choice={choice} onChange={change} />}
      <StatsCards
        stats={stats ?? { companies: null, rounds: null, billing: null }}
      />
    </div>
  )
}
