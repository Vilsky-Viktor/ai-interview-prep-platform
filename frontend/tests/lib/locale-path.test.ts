import { describe, expect, it } from "vitest"

import {
  isLocalizedPath,
  isPrivatePath,
  languageAlternates,
  localizeHref,
  localizedPath,
  splitLocale,
} from "@/lib/locale-path"

describe("localizedPath", () => {
  it("keeps English without a prefix", () => {
    expect(localizedPath("en", "/pricing")).toBe("/pricing")
    expect(localizedPath("en", "/")).toBe("/")
  })

  it("puts other languages under their prefix, the home page at the prefix itself", () => {
    expect(localizedPath("de", "/pricing")).toBe("/de/pricing")
    expect(localizedPath("fil", "/")).toBe("/fil")
  })
})

describe("languageAlternates", () => {
  it("names only the given languages, English always the default", () => {
    expect(languageAlternates("/guides/x", ["en", "de"])).toEqual({
      en: "/guides/x",
      de: "/de/guides/x",
      "x-default": "/guides/x",
    })
  })

  it("names every language's address and English as the default", () => {
    const links = languageAlternates("/faq")

    expect(links.en).toBe("/faq")
    expect(links.ar).toBe("/ar/faq")
    expect(links["x-default"]).toBe("/faq")
    // 23 languages and the default.
    expect(Object.keys(links)).toHaveLength(24)
  })
})

describe("isLocalizedPath", () => {
  it("covers the listed pages and every article", () => {
    expect(isLocalizedPath("/tests")).toBe(true)
    expect(isLocalizedPath("/guides")).toBe(true)
    expect(isLocalizedPath("/guides/hiring-engineers")).toBe(true)
    expect(isLocalizedPath("/compare/testgorilla")).toBe(true)
  })

  it("leaves other pages with one address", () => {
    expect(isLocalizedPath("/tests/backend-developer")).toBe(false)
    expect(isLocalizedPath("/privacy")).toBe(false)
    expect(isLocalizedPath("/guides/../privacy")).toBe(false)
  })
})

describe("localizeHref", () => {
  it("keeps a link in the address's language when its target has that version", () => {
    expect(localizeHref("de", "/faq")).toBe("/de/faq")
    expect(localizeHref("de", "/")).toBe("/de")
    expect(localizeHref("fr", "/guides/hiring-engineers")).toBe(
      "/fr/guides/hiring-engineers"
    )
    expect(localizeHref("de", "/practice?q=sql#list")).toBe(
      "/de/practice?q=sql#list"
    )
  })

  it("leaves other targets, and links on a plain address, as they are", () => {
    expect(localizeHref("de", "/privacy")).toBe("/privacy")
    expect(localizeHref("de", "https://example.com")).toBe(
      "https://example.com"
    )
    expect(localizeHref(null, "/faq")).toBe("/faq")
  })
})

describe("splitLocale", () => {
  it("finds the language and page of a localized address", () => {
    expect(splitLocale("/de/pricing")).toEqual({
      locale: "de",
      path: "/pricing",
    })
    expect(splitLocale("/fr")).toEqual({ locale: "fr", path: "/" })
    expect(splitLocale("/uk/practice/")).toEqual({
      locale: "uk",
      path: "/practice",
    })
  })

  it("leaves English's prefix, unknown prefixes and pages without language versions alone", () => {
    expect(splitLocale("/en/pricing")).toBeNull()
    expect(splitLocale("/xx/pricing")).toBeNull()
    expect(splitLocale("/de/companies")).toBeNull()
    expect(splitLocale("/de/practice/backend-developer")).toBeNull()
    expect(splitLocale("/de/guides/hiring-engineers")).toEqual({
      locale: "de",
      path: "/guides/hiring-engineers",
    })
    expect(splitLocale("/pricing")).toBeNull()
  })
})

describe("isPrivatePath", () => {
  it("marks signed-in areas and personal links", () => {
    expect(isPrivatePath("/companies")).toBe(true)
    expect(isPrivatePath("/companies/1/interviews")).toBe(true)
    expect(isPrivatePath("/apply/abc")).toBe(true)
    expect(isPrivatePath("/practice/backend-developer/start")).toBe(true)
  })

  it("leaves public pages, and pages that only begin alike, public", () => {
    expect(isPrivatePath("/practice")).toBe(false)
    expect(isPrivatePath("/practice/backend-developer")).toBe(false)
    expect(isPrivatePath("/pricing")).toBe(false)
    expect(isPrivatePath("/settingsabc")).toBe(false)
  })
})
