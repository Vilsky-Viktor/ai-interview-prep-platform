import { afterEach, describe, expect, it, vi } from "vitest"

import {
  parseStatsChoice,
  savedStatsChoice,
  statsMonths,
  statsYears,
  writeStatsChoice,
} from "@/lib/stats-period"

const NOW = new Date("2027-03-10T12:00:00Z")

describe("statsMonths and statsYears", () => {
  it("offers the last twelve months, newest first, none before launch", () => {
    expect(statsMonths(NOW)).toEqual([
      "2027-03",
      "2027-02",
      "2027-01",
      "2026-12",
      "2026-11",
      "2026-10",
      "2026-09",
      "2026-08",
      "2026-07",
      "2026-06",
      "2026-05",
      "2026-04",
    ])
    expect(statsMonths(new Date("2026-02-01T12:00:00Z"))).toEqual([
      "2026-02",
      "2026-01",
    ])
  })

  it("offers every year since launch, newest first", () => {
    expect(statsYears(NOW)).toEqual(["2027", "2026"])
  })
})

describe("parseStatsChoice", () => {
  it("takes a saved year or month", () => {
    expect(parseStatsChoice('{"allTime":true,"period":"2026"}', NOW)).toEqual({
      allTime: true,
      period: "2026",
    })
    expect(
      parseStatsChoice('{"allTime":false,"period":"2026-07"}', NOW)
    ).toEqual({ allTime: false, period: "2026-07" })
  })

  it("starts at this month without a saved choice or with a broken one", () => {
    const thisMonth = { allTime: false, period: "2027-03" }

    expect(parseStatsChoice("", NOW)).toEqual(thisMonth)
    expect(parseStatsChoice("not json", NOW)).toEqual(thisMonth)
    expect(parseStatsChoice('{"allTime":1,"period":"2026"}', NOW)).toEqual(
      thisMonth
    )
    expect(
      parseStatsChoice('{"allTime":false,"period":"2026-13"}', NOW)
    ).toEqual(thisMonth)
  })
})

describe("saving the choice", () => {
  afterEach(() => vi.unstubAllGlobals())

  it("keeps it in the browser's storage", () => {
    const store = new Map<string, string>()
    vi.stubGlobal("localStorage", {
      getItem: (key: string) => store.get(key) ?? null,
      setItem: (key: string, value: string) => store.set(key, value),
    })

    writeStatsChoice({ allTime: false, period: "2026" })

    expect(parseStatsChoice(savedStatsChoice(), NOW)).toEqual({
      allTime: false,
      period: "2026",
    })
  })

  it("works without storage, as in a private window", () => {
    vi.stubGlobal("localStorage", {
      getItem: () => {
        throw new Error("blocked")
      },
      setItem: () => {
        throw new Error("blocked")
      },
    })

    expect(() =>
      writeStatsChoice({ allTime: true, period: "2026" })
    ).not.toThrow()
    expect(savedStatsChoice()).toBe("")
  })
})
