import { describe, expect, it } from "vitest"

import { clock, warningSeconds } from "@/lib/countdown"

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

describe("clock", () => {
  it("shows minutes and two-digit seconds", () => {
    expect(clock(65)).toBe("1:05")
    expect(clock(600)).toBe("10:00")
  })

  it("shows under a minute as zero minutes", () => {
    expect(clock(9)).toBe("0:09")
    expect(clock(0)).toBe("0:00")
  })
})
