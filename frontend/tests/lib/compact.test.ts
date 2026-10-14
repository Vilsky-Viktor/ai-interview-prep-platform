import { describe, expect, it } from "vitest"

import { compactNumber, compactPrice } from "@/lib/format"

describe("short numbers", () => {
  it("keeps small numbers whole and shortens large ones", () => {
    expect(compactNumber(950, "en")).toBe("950")
    expect(compactNumber(1500, "en")).toBe("1.5K")
    expect(compactNumber(250_000, "en")).toBe("250K")
    expect(compactNumber(1_234_567, "en")).toBe("1.2M")
    // In each language's own way.
    expect(compactNumber(1500, "de")).toBe("1500")
    expect(compactNumber(1500, "ru")).toBe("1,5 тыс.")
  })

  it("keeps money exact below $1,000 and shortens it from there", () => {
    expect(compactPrice(6660, "USD", "en")).toBe("$66.60")
    expect(compactPrice(1_230_000, "USD", "en")).toBe("$12.3K")
  })
})
