import { describe, expect, it } from "vitest"

import { warningSeconds } from "@/lib/countdown"

describe("warningSeconds", () => {
  it("warns for the last 10 seconds of a long question", () => {
    expect(warningSeconds(60)).toBe(10)
    expect(warningSeconds(30)).toBe(10)
  })

  it("warns only for the last third of a short question", () => {
    expect(warningSeconds(10)).toBe(3)
    expect(warningSeconds(20)).toBe(6)
  })

  it("warns for at least the last second", () => {
    expect(warningSeconds(2)).toBe(1)
  })
})
