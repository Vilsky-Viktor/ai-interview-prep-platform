import { describe, expect, it } from "vitest"

import {
  formatDate,
  formatDay,
  formatPrice,
  formatPriceRange,
  today,
} from "@/lib/format"

// Intl puts no-break spaces in some languages' numbers and currencies.
function plain(text: string) {
  return text.replace(/[  ]/g, " ")
}

describe("formatDate", () => {
  // Midday UTC: the same day in every time zone the tests may run in.
  const iso = "2026-03-05T12:00:00Z"

  it("writes a medium date in the language asked", () => {
    expect(formatDate(iso, "en")).toBe("Mar 5, 2026")
    expect(formatDate(iso, "de")).toBe("05.03.2026")
  })
})

describe("formatDay", () => {
  it("writes the day itself, whatever the time zone", () => {
    expect(formatDay("2026-03-05", "en")).toBe("Mar 5, 2026")
    expect(formatDay("2026-03-05", "de")).toBe("05.03.2026")
  })
})

describe("today", () => {
  it("is the local day as a date field takes it", () => {
    expect(today(new Date(2026, 0, 9, 23, 30))).toBe("2026-01-09")
    expect(today(new Date(2026, 11, 31, 0, 5))).toBe("2026-12-31")
  })
})

describe("formatPrice", () => {
  it("leaves out the cents of a whole amount", () => {
    expect(formatPrice(2400, "USD", "en")).toBe("$24")
    expect(formatPrice(100000, "USD", "en")).toBe("$1,000")
  })

  it("shows the cents of an amount that has them", () => {
    expect(formatPrice(2450, "USD", "en")).toBe("$24.50")
    expect(formatPrice(99, "USD", "en")).toBe("$0.99")
  })

  it("follows the language's way of writing money", () => {
    expect(plain(formatPrice(2450, "EUR", "de"))).toBe("24,50 €")
    expect(plain(formatPrice(2400, "EUR", "de"))).toBe("24 €")
  })
})

describe("formatPriceRange", () => {
  it("writes a price range as the language does", () => {
    expect(plain(formatPriceRange(100, 300, "USD", "en"))).toBe("$1 – $3")
    expect(plain(formatPriceRange(100, 300, "USD", "de"))).toBe("1–3 $")
  })

  it("shows cents when either end has them", () => {
    expect(plain(formatPriceRange(50, 300, "USD", "en"))).toBe("$0.50 – $3.00")
  })
})
