import { describe, expect, it } from "vitest"

import { formatDate, formatPrice } from "@/lib/format"

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
