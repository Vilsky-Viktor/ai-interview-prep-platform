import { describe, expect, it } from "vitest"

import { verdict } from "@/lib/rounds"

describe("verdict", () => {
  it("is hidden while the candidate may not see results", () => {
    expect(verdict(null)).toBe("answered")
  })

  it("is right or wrong for an answer with all or none of its point", () => {
    expect(verdict(true, 100)).toBe("correct")
    expect(verdict(false, 0)).toBe("incorrect")
    expect(verdict(false)).toBe("incorrect")
  })

  it("is partly right for a multi-answer answer with some of its point", () => {
    expect(verdict(false, 67)).toBe("partlyCorrect")
  })
})
