import { afterEach, describe, expect, it, vi } from "vitest"

import {
  previewSignature,
  validPreviewSignature,
} from "@/lib/preview-signature"

describe("previewSignature", () => {
  afterEach(() => vi.unstubAllEnvs())

  it("accepts the signature of the same title and language only", () => {
    vi.stubEnv("PREVIEW_SECRET", "secret")
    const signed = previewSignature("pricing", "en")

    expect(validPreviewSignature("pricing", "en", signed)).toBe(true)
    expect(validPreviewSignature("Something else", "en", signed)).toBe(false)
    expect(validPreviewSignature("pricing", "de", signed)).toBe(false)
    expect(validPreviewSignature("pricing", "en", "")).toBe(false)
  })

  it("depends on the secret", () => {
    vi.stubEnv("PREVIEW_SECRET", "one")
    const signed = previewSignature("pricing", "en")
    vi.stubEnv("PREVIEW_SECRET", "two")

    expect(validPreviewSignature("pricing", "en", signed)).toBe(false)
  })
})
