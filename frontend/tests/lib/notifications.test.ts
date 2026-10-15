import { afterEach, describe, expect, it, vi } from "vitest"

vi.mock("@/lib/api", () => ({ authHeaders: async () => ({}) }))

import { watchNotifications } from "@/lib/notifications"

afterEach(() => {
  vi.unstubAllGlobals()
  vi.useRealTimers()
})

describe("watchNotifications", () => {
  it("asks for the companies fresh on its first connect only", async () => {
    vi.useFakeTimers()
    const controller = new AbortController()
    const asked: string[] = []
    // Each stream ends at once, as the server ends one after its few minutes.
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) => {
        asked.push(url)

        if (asked.length === 2) {
          controller.abort()
        }

        return new Response("")
      })
    )

    const watching = watchNotifications(
      controller.signal,
      () => {},
      () => {},
      true
    )
    await vi.runAllTimersAsync()
    await watching

    expect(asked).toEqual([
      "/api/notifications/me/stream?fresh=true",
      "/api/notifications/me/stream",
    ])
  })
})
