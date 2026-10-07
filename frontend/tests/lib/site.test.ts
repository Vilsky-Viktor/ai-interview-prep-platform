import { describe, expect, it, vi } from "vitest"

import { previewImage } from "@/lib/site"

// lib/site.ts also reads request headers and translations for pages; previewImage uses neither.
vi.mock("next/headers", () => ({ headers: vi.fn() }))
vi.mock("next-intl/server", () => ({ getTranslations: vi.fn() }))

describe("previewImage", () => {
  it("draws a page's title in its language", () => {
    const [image] = previewImage("preise", "de")
    const url = new URL(image.url)

    expect(url.pathname).toBe("/preview")
    expect(url.searchParams.get("title")).toBe("preise")
    expect(url.searchParams.get("lang")).toBe("de")
    expect(image).toMatchObject({ width: 1200, height: 630 })
  })

  it("keeps the site's own picture without a title", () => {
    expect(new URL(previewImage()[0].url).pathname).toBe("/opengraph-image")
  })

  it("keeps the site's own picture in a language it can't draw", () => {
    for (const locale of ["ar", "fa", "he", "hi"]) {
      expect(new URL(previewImage("title", locale)[0].url).pathname).toBe(
        "/opengraph-image"
      )
    }
  })
})
