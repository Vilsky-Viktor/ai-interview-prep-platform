import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { PUBLIC_REVALIDATE_SECONDS } from "@/constants/api"
import { publicFetch, serverFetch } from "@/lib/server-api"

// A signed-in visitor: the token cookie is there.
vi.mock("next/headers", () => ({
  cookies: async () => ({ get: () => ({ value: "token" }) }),
}))
vi.mock("next-intl/server", () => ({ getLocale: async () => "de" }))

const fetchMock = vi.fn()

beforeEach(() => {
  fetchMock.mockResolvedValue(Response.json({ ok: true }))
  vi.stubGlobal("fetch", fetchMock)
})

afterEach(() => {
  vi.unstubAllGlobals()
  fetchMock.mockReset()
})

function sent(): RequestInit & { next?: { revalidate: number } } {
  return fetchMock.mock.calls[0][1]
}

describe("publicFetch", () => {
  it("keeps a copy for every visitor and gives up on a slow service", async () => {
    expect(await publicFetch("/billing/catalog")).toEqual({ ok: true })

    const init = sent()
    expect(init.headers).toEqual({ "Accept-Language": "de" })
    expect(init.next).toEqual({ revalidate: PUBLIC_REVALIDATE_SECONDS })
    expect(init.signal).toBeInstanceOf(AbortSignal)
    expect(init.cache).toBeUndefined()
  })

  it("is null for a missing resource and throws on a failure", async () => {
    fetchMock.mockResolvedValueOnce(new Response(null, { status: 404 }))
    expect(await publicFetch("/rounds/help/legal/x")).toBeNull()

    fetchMock.mockResolvedValueOnce(new Response(null, { status: 503 }))
    await expect(publicFetch("/billing/catalog")).rejects.toThrow("503")
  })
})

describe("serverFetch", () => {
  it("asks fresh, as the user", async () => {
    await serverFetch("/companies/companies")

    const init = sent()
    expect(init.cache).toBe("no-store")
    expect(init.next).toBeUndefined()
    expect(init.headers).toMatchObject({ Authorization: "Bearer token" })
  })
})
