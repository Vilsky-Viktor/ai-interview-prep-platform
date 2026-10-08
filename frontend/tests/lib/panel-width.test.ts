import { afterEach, describe, expect, it, vi } from "vitest"

import {
  clampPanelWidth,
  maxPanelWidth,
  savedPanelWidth,
  savePanelWidth,
} from "@/lib/panel-width"

afterEach(() => {
  vi.unstubAllGlobals()
})

describe("the panel's width", () => {
  it("is at most 900px, or 70% of a smaller window", () => {
    expect(maxPanelWidth(2000)).toBe(900)
    expect(maxPanelWidth(1000)).toBe(700)
    // Never under the narrowest.
    expect(maxPanelWidth(400)).toBe(360)
  })

  it("is kept between the narrowest and the widest", () => {
    expect(clampPanelWidth(200, 1280)).toBe(360)
    expect(clampPanelWidth(500.4, 1280)).toBe(500)
    expect(clampPanelWidth(1200, 1280)).toBe(896)
    expect(clampPanelWidth(1200, 2000)).toBe(900)
  })

  it("is remembered, and the default without a saved one or storage", () => {
    const items = new Map<string, string>()
    vi.stubGlobal("localStorage", {
      getItem: (key: string) => items.get(key) ?? null,
      setItem: (key: string, value: string) => void items.set(key, value),
    })
    expect(savedPanelWidth()).toBe(448)
    savePanelWidth(600)
    expect(savedPanelWidth()).toBe(600)

    vi.stubGlobal("localStorage", undefined)
    expect(savedPanelWidth()).toBe(448)
    expect(() => savePanelWidth(500)).not.toThrow()
  })
})
