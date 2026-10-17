import { afterEach, describe, expect, it, vi } from "vitest"

import { notClosed, rememberClosed } from "@/lib/legal-banner"

const TERMS = { document: "terms", version: "2026-12-01" }
const PRIVACY = { document: "privacy", version: "2026-12-01" }

/** A Storage kept in a map. */
function memory() {
  const items = new Map<string, string>()

  return {
    getItem: (name: string) => items.get(name) ?? null,
    setItem: (name: string, value: string) => void items.set(name, value),
  }
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe("the legal banner", () => {
  it("stays closed for the version it was closed for only", () => {
    vi.stubGlobal("localStorage", memory())

    rememberClosed(TERMS)

    expect(notClosed([TERMS, PRIVACY])).toEqual([PRIVACY])
    expect(notClosed([{ ...TERMS, version: "2027-03-01" }])).toHaveLength(1)
  })

  it("shows every change while the browser keeps nothing", () => {
    const failing = () => {
      throw new Error("blocked")
    }
    vi.stubGlobal("localStorage", { getItem: failing, setItem: failing })

    rememberClosed(TERMS)

    expect(notClosed([TERMS, PRIVACY])).toEqual([TERMS, PRIVACY])
  })
})
